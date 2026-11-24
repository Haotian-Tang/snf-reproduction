# CBIO7501 capstone requirements

Sources checked on 2026-11-24:

- [Capstone rubric](https://khanlab.bio/cbio7501-f26/assessment/capstone-rubric.html)
- [Lesson 11: Documentation](https://khanlab.bio/cbio7501-f26/pages/11-documentation.html)
- [Lesson 12: Putting it all together](https://khanlab.bio/cbio7501-f26/pages/12-putting-it-together.html)
- [Partner report template](https://khanlab.bio/cbio7501-f26/assessment/reproduce-report-template.html)

The capstone is separate from LTEE: one existing or manageable analysis in
its own GitHub repository. It can be public or private. Private projects
must grant the instructor and reproduction partner access. A GitHub release
and the partner's actual reproduce report are required. A Zenodo DOI is
optional for this capstone. The course notes that rubric weights remain
subject to confirmation; the official syllabus governs deadlines and policy.

| Rubric area | Listed points | Evidence in this project |
| --- | ---: | --- |
| Reproduce from a clean clone | 25 | `pixi install --locked`, `pixi run reproduce`, Reproduce CI on released tag; partner report still requires a classmate |
| Organization and data | 15 | Separate data/raw, metadata, scripts, config, results, reports and docs; scripted downloads, SHA256, read-only files; no generated outputs or raw data in Git |
| Software environment | 15 | Committed pixi.toml and pixi.lock, honest supported platforms; lock-based container recipe |
| Automation | 15 | Pixi dependency tasks run download -> report/recalculation -> validation -> provenance, plus citation and failure-path checks |
| Literate report | 10 | Executed Quarto R report, computed inline numbers/tables/figures, captions, alt text, session versions |
| Version control | 10 | Actual commits, pull request, released tag; original analysis preserved in the first commit |
| Documentation and openness | 10 | README's seven questions, code/text/data terms, valid CITATION.cff, data availability statement |

The rubric explicitly accepts Pixi tasks or a workflow manager. Duplicating
this small analysis in both Snakemake and Nextflow is not necessary to meet
the automation criterion. The R analysis runs during report rendering so
figures and numbers cannot remain stale while prose is rebuilt.

Run `pixi run check-capstone` for the instructor's automatic checks, copied
without functional changes from the course. Its DOI line will say NO when
there is no Zenodo DOI: this is an optional item for capstones, as the
checker text itself states. Automatic checks do not constitute a grade or
independent partner review.

## Remaining human requirement

A classmate must clone the released repository, follow only the README and
file a real reproduce report using the issue template. Their report is not
generated or signed by this workflow. Fix any problems they identify, make
the final submission release, and submit the repository/release/report
links through the instructor's required channel. The project does not claim
this swap has occurred until that evidence exists.
