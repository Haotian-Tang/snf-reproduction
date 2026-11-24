"""Write revision, environment, input and output provenance after verification."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def checksum(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def git(*args):
    result = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return os.environ.get("SNF_REVISION", "unavailable") if args == ("rev-parse", "HEAD") else "unavailable"


def main():
    paths = [ROOT / "pixi.toml", ROOT / "pixi.lock", ROOT / "config/analysis.json", ROOT / "_quarto.yml"]
    paths += sorted((ROOT / "scripts").glob("*.R")) + sorted((ROOT / "scripts").glob("*.py"))
    paths += sorted((ROOT / "reports").glob("*.qmd"))
    paths += sorted((ROOT / "reports").glob("*.bib"))
    paths += [p for p in sorted((ROOT / "metadata").iterdir()) if p.is_file()]
    output = ROOT / "results"
    generated = [p for p in sorted(output.iterdir()) if p.is_file() and p.name != "provenance.json"]
    generated.append(ROOT / "reports/snf-report.html")
    record = {
        "completed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": git("rev-parse", "HEAD"),
        "git_status": git("status", "--porcelain"),
        "platform": platform.platform(), "machine": platform.machine(), "python": sys.version,
        "source_sha256": {str(p.relative_to(ROOT)): checksum(p) for p in paths},
        "verified_inputs": json.loads((ROOT / "metadata/sources.json").read_text()),
        "validation": json.loads((output / "validation.json").read_text()),
        "output_sha256": {str(p.relative_to(ROOT)): checksum(p) for p in generated},
    }
    (output / "provenance.json").write_text(json.dumps(record, indent=2) + "\n")
    print("Reproduction complete: reports/snf-report.html and results/provenance.json")


if __name__ == "__main__":
    main()
