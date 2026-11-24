# Decisions

## 2026-11-24 - Scope and history

Pause work on the course LTEE example and turn the existing SNF breast-cohort
homework reanalysis into a separate capstone. Preserve the original analysis
sources in the initial Git commit, dated when committed; do not fabricate a
past course history. Existing homework PDFs and output files remain local
and ignored. There was no pre-existing Git repository for this directory.

## 2026-11-24 - Keep the scientific mismatch visible

Retain the original inputs, methods, seed and primary settings. Published
p-values and the original reanalysis targets are separate metadata. Do not
select parameters to make the result match the paper. Compare partitions
independently of their arbitrary labels, and distinguish exact reruns from
parameter sensitivity and from reproducing a publication's conclusion.

## 2026-11-24 - Small workflow, executed report

Use Pixi tasks, explicitly accepted by the capstone rubric, rather than
maintaining two workflow engines for a single small cohort. Quarto invokes
the R analysis at every render; validation and provenance follow it. No
report cache or manually pasted statistics. Original SNFtool source stays
unmodified and is downloaded, checked and sourced at runtime.

## 2026-11-24 - Platforms and rights

Lock Linux x86-64 and Apple Silicon macOS environments. Windows users can
use WSL2; Intel macOS and Linux ARM are not advertised as tested native
environments. Cross-platform claims require the same reference checks to
pass, not just a successful installation. Keep publisher data and software
out of Git, distinguish GPL software from data rights, and do not assign an
invented open data license.

## 2026-11-24 - Independent review

Automated local, container and CI checks are evidence of automated
reproduction only. The classmate swap and report remain a human step. AI
assistance is disclosed without asserting that a person reviewed anything
they have not reviewed.
