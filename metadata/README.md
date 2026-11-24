# Input metadata and reference checks

- `sources.json`: publisher download URLs, publication DOI, archive hashes,
  first download date and separate rights statements for data, code and PDF.
- `downloads.sha256`: the same archive hashes in standard SHA256 format.
- `inputs.sha256`: original cohort files and original R source hashes;
  destinations are under read-only, ignored `data/raw/`.
- `reference.json`: small regression targets from the 2026-10-23 homework
  run (R 4.6.1, survival 3.8-12, Apple R BLAS). These are **our reanalysis**
  results, not a reconstruction of unavailable published cluster labels.

The primary expected SNF p-value is 0.00700584185234621. Cluster sizes are
19, 19, 20, 23, 24 when sorted. Validation also checks the identities of all
four partitions using SHA256 of their pairwise coassignment matrices, the
ordered patient hash, every sensitivity-grid p-value and ARI, matrix
invariants and numerical summaries. Absolute p-value tolerance is 1e-8;
matrix-summary tolerance is 1e-8. Cluster label permutations are allowed.

Report and PNG bytes are not regression targets: graphics devices, fonts,
timestamps and embedded session paths may vary by platform. Every run
records its actual output hashes for traceability.

Metadata is small and tracked; downloads, extracted data, environments and
generated results are ignored by Git. Data field meanings are documented in
`docs/methods.md` and source licensing in `docs/data-availability.md`.
