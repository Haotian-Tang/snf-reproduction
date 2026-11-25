# Locked Linux container

The image contains this source tree and the linux-64 environment from
`pixi.lock`. It is built locally or in the repository's CI; no
container registry account is needed. Docker Desktop must be running.

From a clean clone at the release tag:

```bash
docker build --platform linux/amd64 --provenance=false \
  -f containers/Dockerfile -t snf-reproduction:1.0.0 .
docker run --platform linux/amd64 --name snf-check snf-reproduction:1.0.0
docker cp snf-check:/project/reports/snf-report.html ./snf-container-report.html
docker cp snf-check:/project/results ./snf-container-results
docker rm snf-check
```

Use a different container name if `snf-check` already exists. The run starts
without data: it downloads, verifies and computes everything. `docker cp`
retrieves the completed report and verification evidence, and `docker rm`
removes this named container after copying. The copied outputs are not meant
to be committed. Allow additional disk for image layers and downloads.
On Apple Silicon the x86-64 image uses emulation and can be slower than the
native Pixi environment. Linux ARM is not a native lock target.

CI passes its revision through the optional `VCS_REF` build argument; a
manual build without it records the revision as unavailable, alongside
actual source/configuration/lock hashes. The image pins the Pixi base by
digest and installs with `--locked`; it does not resolve a new environment.
