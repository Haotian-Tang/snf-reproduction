"""Download immutable publication supplements and verify archives and inputs.

Existing mismatching files are never silently replaced. Remove the named bad
file yourself, then rerun. Only files named in metadata/inputs.sha256 are
extracted; archive paths cannot choose a destination outside data/raw/.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def verify(path: Path, expected: str) -> None:
    if not path.is_file():
        raise ValueError(f"Missing input: {path}")
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"SHA256 mismatch: {path}\nexpected {expected}\nactual   {actual}\n"
                         "Remove this file and rerun `pixi run download` to restore it.")


def inputs(root: Path) -> list[tuple[str, Path]]:
    entries = []
    for line in (root / "metadata/inputs.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = root / name
        if not path.resolve().is_relative_to((root / "data/raw").resolve()):
            raise ValueError(f"Input destination outside data/raw: {name}")
        entries.append((digest, path))
    return entries


def download(url: str, destination: Path, digest: str) -> None:
    if destination.exists():
        verify(destination, digest)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": "SNF-reproduction/1.0 (academic reproducibility)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=90) as source, partial.open("wb") as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
            verify(partial, digest)
            partial.replace(destination)
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
            partial.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
    destination.chmod(0o444)


def extract_member(archive: zipfile.ZipFile, member: str, destination: Path, digest: str) -> None:
    if destination.exists():
        verify(destination, digest)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_suffix(destination.suffix + ".partial")
        try:
            with archive.open(member) as source, partial.open("wb") as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
            verify(partial, digest)
            partial.replace(destination)
        finally:
            partial.unlink(missing_ok=True)
    destination.chmod(0o444)


def main(root: Path = ROOT) -> None:
    sources = json.loads((root / "metadata/sources.json").read_text())
    assets = {asset["id"]: asset for asset in sources["assets"]}
    for asset in sources["assets"]:
        destination = root / asset["path"]
        if not destination.resolve().is_relative_to((root / "data/raw").resolve()):
            raise ValueError("Archive destination must be inside data/raw")
        print(f"Verify/download {asset['id']}", flush=True)
        download(asset["url"], destination, asset["sha256"])
        destination.chmod(0o444)
    with zipfile.ZipFile(root / assets["processed-data"]["path"]) as data_archive, \
            zipfile.ZipFile(root / assets["software"]["path"]) as code_archive:
        for digest, destination in inputs(root):
            member = destination.relative_to(root / "data/raw").as_posix()
            archive = data_archive if member.startswith("Breast/") else code_archive
            extract_member(archive, member, destination, digest)
    verify_inputs(root)


def verify_inputs(root: Path = ROOT) -> None:
    for digest, path in inputs(root):
        verify(path, digest)
        if os.stat(path).st_mode & 0o222:
            raise ValueError(f"Raw input should be read-only: {path}")
    print("All original input checksums pass; raw files are read-only.")


if __name__ == "__main__":
    verify_inputs() if sys.argv[1:] == ["--verify-only"] else main()
