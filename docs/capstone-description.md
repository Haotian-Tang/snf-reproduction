# Reproducible Similarity Network Fusion Analysis of TCGA Breast Cancer Data

**Haotian Tang | CBIO7501 Capstone Project**

## Project description

This project provides a reproducible reanalysis of 105 TCGA breast cancer
patients using similarity network fusion (SNF) to integrate mRNA expression,
DNA methylation, and miRNA data. It reconstructs patient similarity networks,
compares single-omics and fused-network clustering, examines survival
associations, and evaluates parameter sensitivity. A locked Pixi environment,
automated data verification, executable Quarto report, and continuous
integration support one-command reproduction while documenting differences
from the original publication.

## Scientific question

How do patient groupings and their overall-survival associations differ
between individual omics and SNF integration, and how stable are these
results under changes in network-construction and fusion parameters?

## GitHub Repo

[Haotian-Tang/snf-reproduction](https://github.com/Haotian-Tang/snf-reproduction)

## Data used and its license

The project uses the author-processed TCGA breast cohort supplied with
Wang et al. (2014), [doi:10.1038/nmeth.2810](https://doi.org/10.1038/nmeth.2810),
Supplementary Data MOESM206: matched mRNA expression (17,814 features),
DNA methylation (23,094 probes), miRNA expression (354 features), and
survival information for 105 patients. Raw TCGA preprocessing is outside
the project scope.

**Data license:** The publisher makes these supplements publicly
downloadable, but no explicit standalone open-data reuse license was
identified. The data retain their original publisher/source terms and are
downloaded directly by the workflow; patient-level source tables are not
redistributed in GitHub.

**Software licenses:** The original SNFtool 1.2 attachment states GPL
(version unspecified). Our workflow code is MIT licensed; original report
and documentation text are CC BY 4.0. These licenses do not relicense the data.
