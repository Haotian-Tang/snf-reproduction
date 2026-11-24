# Pixi 0.83.0; immutable multi-platform manifest, linux/amd64 selected at build.
FROM ghcr.io/prefix-dev/pixi:0.83.0@sha256:3dce86c6e87371c58035aa41b09f2b56ca8f011722320551e0c2bfc1c59da5fb
WORKDIR /project
COPY pixi.toml pixi.lock ./
RUN pixi install --locked
COPY . .
ARG VCS_REF=unavailable
ENV SNF_REVISION=${VCS_REF}
LABEL org.opencontainers.image.source="https://github.com/Haotian-Tang/snf-reproduction"
LABEL org.opencontainers.image.revision=${VCS_REF}
CMD ["pixi", "run", "--locked", "reproduce"]
