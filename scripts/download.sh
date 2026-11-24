#!/bin/sh
# Run from the project root. curl and unzip required; originals remain unchanged.
set -eu
mkdir -p data/downloads data/original vendor
base='https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fnmeth.2810/MediaObjects'
fetch() {
  if [ ! -f "$2" ]; then
    curl --fail --location --retry 3 "$1" -o "$2.partial"
    mv "$2.partial" "$2"
  fi
}
fetch "$base/41592_2014_BFnmeth2810_MOESM206_ESM.zip" data/downloads/supplementary-data.zip
fetch "$base/41592_2014_BFnmeth2810_MOESM205_ESM.zip" data/downloads/supplementary-software.zip
fetch "$base/41592_2014_BFnmeth2810_MOESM204_ESM.pdf" data/downloads/supplementary-methods.pdf
# Verify archives before extraction. sha256sum is available on Linux; macOS has shasum.
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum -c checksums-downloads.sha256
else
  shasum -a 256 -c checksums-downloads.sha256
fi
unzip -q -o data/downloads/supplementary-data.zip 'Breast/*' -d data/original
unzip -q -o data/downloads/supplementary-software.zip 'SNFtool/*' -d vendor
