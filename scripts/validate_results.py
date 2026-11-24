"""Compare scientific results with the documented reference, allowing label swaps."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def partition_hash(labels: list[str]) -> str:
    return hashlib.sha256(bytes(int(a == b) for a in labels for b in labels)).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(actual: float, expected: float, tolerance: float, name: str) -> None:
    if not math.isfinite(actual) or abs(actual - expected) > tolerance:
        raise ValueError(f"{name}: got {actual}, expected {expected} +/- {tolerance}")


def main() -> None:
    config = json.loads((ROOT / "config/analysis.json").read_text())
    reference = json.loads((ROOT / "metadata/reference.json").read_text())
    output = ROOT / config["results_dir"]
    checks = []

    def require(condition: bool, name: str) -> None:
        if not condition:
            raise ValueError(name)
        checks.append(name)

    qc = read_rows(output / "data_qc.tsv")
    require({r["view"]: int(r["features"]) for r in qc} == reference["features"], "All input feature counts match")
    require(all(int(r["patients"]) == reference["patients"] and int(r["missing"]) == 0 for r in qc),
            "All views have the complete reference cohort and no missing data")
    patients = read_rows(output / "patient_clusters.tsv")
    require(len(patients) == reference["patients"], "Patient count matches")
    require(len({r["patient"] for r in patients}) == len(patients), "Patient identifiers are unique")
    ordered_ids = "\n".join(r["patient"] for r in patients) + "\n"
    require(hashlib.sha256(ordered_ids.encode()).hexdigest() == reference["patient_order_sha256"],
            "Patient identity and order match the reference")
    require(sum(int(r["Death"]) for r in patients) == reference["deaths"], "Survival event count matches")
    metrics = read_rows(output / "survival_comparison.tsv")
    require({r["method"] for r in metrics} == set(reference["methods"]), "All four methods are present")
    tolerance = config["validation"]["p_absolute_tolerance"]
    for row in metrics:
        method = row["method"]
        expected = reference["methods"][method]
        close(float(row["logrank_p"]), expected["logrank_p"], tolerance, method + " log-rank p")
        labels = [r[method] for r in patients]
        sizes = sorted(labels.count(label) for label in set(labels))
        require(sizes == expected["sorted_cluster_sizes"], method + " group sizes match")
        require(partition_hash(labels) == expected["partition_sha256"], method + " partition matches up to label permutation")
        close(float(row["paper_p"]), config["paper"]["logrank_p"][method], 0, method + " paper comparison")
    repeatability = {r["check"]: float(r["value"]) for r in read_rows(output / "repeatability.tsv")}
    close(repeatability["network_max_abs_difference"], 0, config["validation"]["matrix_tolerance"], "Repeated network")
    require(repeatability["partition_pairwise_identical"] == 1, "Repeated partition is identical")

    def grid_key(row):
        return row["distance"], int(row["iterations"]), int(row["K"])

    diagnostics = {grid_key(r): r for r in read_rows(output / "diagnostics.tsv")}
    require(set(diagnostics) == {grid_key(r) for r in reference["diagnostics"]}, "The complete diagnostic grid is present")
    for expected in reference["diagnostics"]:
        actual = diagnostics[grid_key(expected)]
        close(float(actual["logrank_p"]), expected["logrank_p"], tolerance, str(grid_key(expected)) + " p")
        close(float(actual["ARI_to_primary"]), expected["ARI_to_primary"], 1e-10, str(grid_key(expected)) + " ARI")
    checks.append("Every diagnostic p-value and ARI matches")
    with (output / "fused_network.tsv").open() as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)[1:]
        records = list(reader)
    require(header == [r["patient"] for r in patients] == [r[0] for r in records], "Network rows and columns match the patient order")
    matrix = [[float(x) for x in row[1:]] for row in records]
    n = len(patients)
    require(len(matrix) == n and all(len(row) == n for row in matrix), "Network dimensions match")
    require(all(math.isfinite(x) and x >= 0 for row in matrix for x in row), "Network is finite and nonnegative")
    require(max(abs(matrix[i][j] - matrix[j][i]) for i in range(n) for j in range(n)) < config["validation"]["matrix_tolerance"],
            "Network is symmetric")
    summaries = {"sum": math.fsum(x for row in matrix for x in row),
                 "sum_squares": math.fsum(x*x for row in matrix for x in row),
                 "trace": math.fsum(matrix[i][i] for i in range(n))}
    for key, value in summaries.items():
        close(value, reference["network"][key], 1e-8, "Network " + key)
    checks.append("Network summaries match the reference within tolerance")
    for name in ["figure1_networks.png", "figure2_embedding_survival.png", "figure3_survival_comparison.png"]:
        require((output / name).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", name + " is a PNG")
    html = (ROOT / "reports/snf-report.html").read_text()
    require(html.count("data:image/png") >= 3, "The HTML report embeds all three figures")
    (output / "validation.json").write_text(json.dumps({"status": "passed", "checks": checks,
                                                      "p_absolute_tolerance": tolerance}, indent=2) + "\n")
    print(f"PASS: {len(checks)} scientific and report checks; all reference partitions and metrics match.")


if __name__ == "__main__":
    main()
