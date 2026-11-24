# Analysis and validation

## Cohort and fields

Wang et al. (2014), DOI 10.1038/nmeth.2810, supplies processed TCGA cancer
data (MOESM206). This project uses only `Breast/`:

| File | Meaning | Dimensions |
| --- | --- | --- |
| `BREAST_Gene_Expression.txt` | Normalized mRNA microarray measurements, features by samples | 17,814 by 105 |
| `BREAST_Methy_Expression.txt` | Normalized DNA methylation measurements, features by samples | 23,094 by 105 |
| `BREAST_Mirna_Expression.txt` | Normalized miRNA measurements, features by samples | 354 by 105 |
| `BREAST_Survival.txt` | `PatientID`, follow-up `Survival` in days, `Death` indicator (1 event, 0 censored) | 105 patients |

Barcode prefixes (first 12 characters) identify patients. Every matrix must
have exactly the same unique patients as the clinical table. The analysis
uses clinical row order throughout and checks completeness, finiteness,
feature counts and 18 death events. The omics tables contain doubled header
tabs and trailing tabs: header tokens and numeric records are parsed as
whitespace-delimited fields to avoid false empty columns. Raw files are
never rewritten. Supplied measurements are already standardized; they are
not log-transformed, filtered, imputed or standardized again.

## Primary analysis

The original SNFtool 1.2 R functions are downloaded from MOESM205, individually
checksummed and sourced without modification. The primary analysis uses
Euclidean distance (`sqrt(dist2(x, x))`), K=20 neighbors, alpha=0.5,
20 fusion iterations, five clusters and random seed 20261023. These settings
are stored in `config/analysis.json`, retained from the original homework.
They are not asserted to be the exact unrecovered BIC execution settings.

Single-omics and fused networks use the original `SpectralClustering`.
`survival::survdiff` supplies a chi-square statistic with number of groups
minus one degrees of freedom; `pchisq(..., lower.tail=FALSE)` gives the
log-rank p-value. Kaplan-Meier plots convert days to months using the
configured divisor. The PCA is calculated from the centered fused matrix.

The diagnostic grid reports all configured combinations of distance
convention, iteration count and neighbors. The squared-distance convention
comes from the original README example. No combination is chosen by its
p-value. Adjusted Rand index describes agreement with the primary partition.

## What a passing check means

`pixi run reproduce` renders the Quarto report. Its first hidden computation
chunk runs the complete analysis afresh; remaining chunks build every table,
inline computed number and figure inclusion from those objects. Caching and
freezing are disabled. The HTML embeds the three PNG figures and can be
opened without an R installation or a network connection.

`scripts/validate_results.py` then checks:

- exact cohort size, feature counts, event count and patient-order hash;
- all four partitions via pairwise coassignment SHA256 hashes, allowing
  arbitrary permutations of group labels;
- primary and diagnostic log-rank p-values (absolute tolerance 1e-8), all
  diagnostic ARIs (1e-10), cluster sizes and the complete diagnostic grid;
- a finite, nonnegative, symmetric 105 by 105 fused matrix, matching patient
  order, and sum, sum of squares and trace within 1e-8 of the reference;
- within-run recomputation of the fused matrix and partition;
- three valid PNG outputs and three embedded figures in the HTML report.

Reference values come from the 2026-10-23 local homework analysis, before
this environment migration. They are summarized and explained in
`metadata/reference.json`; they are not selected anew after inspecting a
rerun. Matrix summary agreement is weaker than comparing every matrix
element with a stored reference, so no cross-platform bitwise identity is
claimed. Full partition hashes provide a stronger check on the main
clustering result than cluster sizes alone.

Changing primary parameters can legitimately change results. `pixi run report`
can render an exploratory configuration, but `pixi run reproduce` must fail
if it no longer agrees with the documented reference. A deliberate change
to a reference requires a described methodological change and a new release;
do not update targets merely to make a failed run green.

## Interpretation limits

The primary SNF p-value is approximately 0.007006; the paper reports 0.0011.
The corresponding single-omics results also differ. This run does not
establish that SNF outperforms all individual omics, and survival significance
does not establish predictive or clinical utility. Exact original cluster
assignments were not identified. Supplementary Table 1 reports 1,046 BIC
miRNA features while the supplied file has 354. These unresolved differences
remain visible in the report rather than being repaired by tuning.
