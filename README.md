# SNF reproduction: TCGA breast cancer

[![Reproduce](https://github.com/Haotian-Tang/snf-reproduction/actions/workflows/reproduce.yml/badge.svg)](https://github.com/Haotian-Tang/snf-reproduction/actions/workflows/reproduce.yml)

Reanalyze the original processed TCGA breast cohort with similarity network
fusion (SNF). Question: can we reproduce the patient networks, clustering and
survival comparisons from the supplied matrices and original R software?
This is Haotian Tang's CBIO7501 capstone, separate from the LTEE project.

One-page project description: [capstone-description.md](docs/capstone-description.md).

**Scope:** a reproducible reanalysis of 105 patients, not an exact recovery of
the paper's result or raw TCGA preprocessing. Our SNF log-rank p-value is
0.00700584; the paper reports 0.0011. The difference remains documented.

## Publication and data

Wang et al. (2014), *Similarity network fusion for aggregating data types on
a genomic scale*, Nature Methods 11:333-337,
[doi:10.1038/nmeth.2810](https://doi.org/10.1038/nmeth.2810).

The publisher's original supplements supply the processed breast data
(MOESM206), SNFtool 1.2 R source (MOESM205) and methods (MOESM204). Sources,
SHA256 values and rights statements are in [metadata](metadata/README.md)
and the [data availability statement](docs/data-availability.md).
Downloads and patient-level inputs are kept out of Git.

## Reproduce

Install [Pixi](https://pixi.prefix.dev/latest/installation/) and Git. This
repository is **public** and can be cloned over HTTPS.

```bash
git clone https://github.com/Haotian-Tang/snf-reproduction.git
cd snf-reproduction
git checkout v1.0.0
pixi install --locked
pixi run reproduce
```

Then open **`reports/snf-report.html`** in a browser. It is a self-contained
HTML report with the figures embedded; it works offline after generation.
The rendered report is also attached to the GitHub release.

One command downloads and checks the inputs, makes raw files read-only,
recomputes the R analysis while rendering Quarto, verifies the reference
results, validates the citation, runs integrity tests and records provenance.
Every tool used for the analysis comes from `pixi.lock`; no system R, CRAN
installation, manual data download or notebook cell order is needed.

First run needs internet access to conda-forge and the publisher. Subsequent
runs reuse the verified downloads. Files with wrong hashes cause a clear
error; remove only the named bad file and rerun `pixi run download`.

## Hardware and platforms

The lock contains **Linux x86-64** and **Apple Silicon macOS** environments.
Linux is checked by GitHub Actions and the container; macOS is checked
locally. Use WSL2 on x86-64 Windows. Other native platforms are not tested.

Allow 4 GB free disk and 4 GB RAM as a conservative budget; the native
environment is approximately 1.7 GB and checked raw inputs approximately
130 MB. One CPU thread is used for numerical libraries; no GPU is needed.
Installation and download time depend on the connection. Measured runtime
and independent checks are recorded in [verification](docs/verification.md).
For a lock-based Linux environment, see [container instructions](containers/README.md).

## Expected output

| Output | Meaning |
| --- | --- |
| `reports/snf-report.html` | Executed report: QC, methods, three figures, survival comparison, sensitivity grid and versions |
| `results/data_qc.tsv` | 105 patients; 17,814 mRNA, 23,094 methylation and 354 miRNA features; no missing values |
| `results/survival_comparison.tsv` | Computed and published log-rank comparisons |
| `results/patient_clusters.tsv` | Patient identities, survival fields and four cluster assignments |
| `results/fused_network.tsv`, `analysis.rds` | Numerical fused matrix and R analysis objects |
| `results/diagnostics.tsv`, `repeatability.tsv` | Complete parameter grid and fixed-setting repeat checks |
| `results/validation.json`, `provenance.json`, `sessionInfo.txt` | Scientific checks, exact revision/input/output hashes and actual software session |

| Method | Expected reanalysis p-value | Paper Table 1 |
| --- | ---: | ---: |
| mRNA | 0.0058764254 | 0.03 |
| DNA methylation | 0.2420016781 | 0.05 |
| miRNA | 0.0094654371 | 0.30 |
| SNF | 0.0070058419 | 0.0011 |

The five SNF groups have sizes **19, 19, 20, 23, 24** (sorted), with **18
deaths** overall. Validation checks complete partitions up to relabeling,
not only group sizes. P-values must match within 1e-8. Image bytes and report
timestamps can differ across systems. See [methods and limits](docs/methods.md).

The supplied miRNA file has 354 features, while Supplementary Table 1 lists
1,046. Exact original BIC settings and cluster labels were not recovered.
This reanalysis does not show SNF outperforming every individual omics.

## Repository contents and settings

| Path | Contents |
| --- | --- |
| `config/analysis.json` | Parameters, seed, expected cohort dimensions and diagnostic grid |
| `metadata/` | Sources, checksums and documented regression targets |
| `scripts/` | Input acquisition, R analysis, validation, provenance and course checker |
| `reports/` | Quarto source and generated HTML (HTML is ignored by Git) |
| `data/raw/` | Downloaded, checked, read-only inputs (ignored) |
| `results/` | Generated outputs; safe to remove and rebuild (ignored) |
| `containers/` | Docker recipe using the Linux lock |
| `docs/`, `tests/`, `.github/` | Decisions, methods, checks, CI and partner report template |

`pixi run report` recomputes the report. `pixi run test` tests error handling.
`pixi run citation` validates CITATION.cff. `pixi run check-capstone` runs the
instructor's checker; its optional DOI line may say NO for this capstone.
The [requirements map](docs/capstone-requirements.md) links each rubric item
to its evidence. [Contributing](CONTRIBUTING.md) explains changes and PRs.

## Cite and license

Cite **Haotian Tang (2026), SNF reproduction: TCGA breast cancer reanalysis,
version 1.0.0**, and cite Wang et al. above. Machine-readable citation is in
[`CITATION.cff`](CITATION.cff); no project DOI is claimed.

Original workflow code/configuration/tests: **MIT** ([LICENSE](LICENSE)).
Original report prose and documentation: **CC BY 4.0**. Downloaded SNFtool:
**GPL**, version unspecified in its DESCRIPTION. Publisher data/PDF retain
their original terms; no explicit standalone open data license was identified.
These materials are downloaded from the source and are not relicensed here.

## Contact and independent reproduction

Haotian Tang: **haotian.tang@mbzuai.ac.ae**. Use a repository issue for a
reproduction problem and include the revision, platform, command and complete
error. A classmate should use the **Reproduce report** issue template after
running a clean clone from this README alone. This repository is prepared
for that swap; an automated run does not replace the classmate's report.

AI assistance: OpenAI Codex helped develop, debug and execute code, inspect
requirements and draft documentation/report text. Automated results do not
claim independent human review.
