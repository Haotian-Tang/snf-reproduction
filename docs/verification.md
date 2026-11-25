# Verification evidence

## Native macOS

On 2026-11-24, the locked Apple Silicon environment (R 4.5.3, survival
3.8-12, OpenBLAS/LAPACK) regenerated the original reanalysis results. All
27 scientific/report checks and five integrity tests passed. All four
partitions matched the 2026-10-23 reference up to cluster label permutation,
as did primary p-values and every prespecified diagnostic p-value and ARI.
This checks a change of R/BLAS environment without changing reference targets.

Measured with `/usr/bin/time -l pixi run reproduce` on the same Apple Silicon
laptop, using the installed environment and already downloaded, reverified
inputs: **65.91 seconds** wall time and **912,785,408 bytes** maximum resident
set size (about 0.85 GiB). This includes report rendering, scientific checks,
citation validation, tests and provenance; it excludes first installation
and initial download. Concurrent machine load and network access can change
the timing. `du -sh` reported 1.7 GB for the environment, 128 MB for raw inputs,
1.3 MB for results and approximately 1 MB for report sources/rendered HTML.

`pixi install --locked` checks manifest/lock consistency. The complete R
session, validation checks, input identifiers and source/output hashes are
written under `results/` on each run. The rendered HTML embeds all three
figures and includes versions; generated outputs are ignored by Git.

## Clean clone and Linux

The [Reproduce workflow](https://github.com/Haotian-Tang/snf-reproduction/actions/workflows/reproduce.yml)
checks a fresh Linux runner and a separately built Linux container on every
push/PR and release tag. Read the checks on the specific tag you reproduce,
not only the latest branch badge. Its artifacts contain the report and
aggregate verification evidence; the release keeps the HTML and JSON checks.
The repository and release assets are publicly available.

## Instructor checker and independent review

`pixi run check-capstone` runs the instructor's checker. All required
automatic items pass locally (19 of 20 total); the optional Zenodo DOI line is NO for this
capstone. The checker does not assess the scientific interpretation or
replace the actual GitHub run results.

A classmate's clean-clone reproduce report is a separate, pending human
requirement. Use the issue template. Local/CI/container checks are automated
evidence and are not presented as an independent classmate review.
