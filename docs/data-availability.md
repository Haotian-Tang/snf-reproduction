# Data and code availability

The original processed TCGA breast cohort is distributed with Wang et al.
(2014), DOI [10.1038/nmeth.2810](https://doi.org/10.1038/nmeth.2810).
`metadata/sources.json` records the three publisher URLs, SHA256 values and
license observations; `metadata/inputs.sha256` identifies each extracted
input and source file. First local download: 2026-10-23.

| Resource | Identifier | Use in this project | License / rights statement |
| --- | --- | --- | --- |
| Supplementary data | MOESM206 | Breast expression, methylation, miRNA and survival tables | Publicly downloadable publisher supplement; no explicit standalone reuse license was identified in the inspected materials. Public access alone does not establish an open license. |
| Supplementary software | MOESM205, SNFtool 1.2 | Original R functions, sourced without modification | DESCRIPTION states `GPL` without a version. The original authors and notices remain in the downloaded attachment. |
| Supplementary methods | MOESM204 | Interpretation of methods, Table 1 and Figure 15 | Publisher supplement; not represented here as Creative Commons material. |

The repository does not redistribute these downloads or the patient-level
tables. The script obtains them directly from the publisher, verifies their
hashes and protects them as read-only. No controlled-access TCGA sequencing
files or credentials are needed. Reusers must check the original terms for
their intended reuse; this project's license grants no additional rights to
third-party material.

Our original code, tests and configuration are MIT licensed. Our original
report prose and documentation are CC BY 4.0. Third-party code and data keep
their own terms. The small aggregate reference values and partition hashes
in `metadata/reference.json` are regression targets for this reanalysis;
they are not original raw data or the paper's unprovided patient labels.

All outputs are generated locally from the checked inputs. GitHub CI keeps
the rendered report and aggregate verification logs as artifacts. A release
can attach the self-contained HTML report; source data remains at its
original publisher location. No Zenodo DOI is claimed or required for this
capstone.
