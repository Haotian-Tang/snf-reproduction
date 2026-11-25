# Contributing

Open an issue with your OS/CPU, Pixi version, Git commit, exact command and
full error. The repository is public; propose changes through a fork and PR.
Never include credentials, controlled-access data or unpublished personal
information in an issue.

Create a branch, make a small described commit, and open a pull request to
`main`. Run `pixi install --locked`, `pixi run reproduce` and
`pixi run check-capstone`; wait for green CI before merging. Keep existing
history. Record methodological decisions in `docs/decisions.md`.

Add dependencies through Pixi and commit manifest/lock changes together.
Keep raw data immutable and outputs out of Git. Change settings in the JSON
configuration. A deliberate reference change needs an explanation of the
methodological reason, independently inspected results and a new release;
do not replace a target simply because a run failed.

For the class swap, use the Reproduce report issue template and only the
README and its links. Record what you actually ran, including any failure.
Do not mark unchecked steps as completed. See `CODE_OF_CONDUCT.md` for
discussion expectations.
