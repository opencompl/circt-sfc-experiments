#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: $0 <input.fir> <output.fir>" >&2
    exit 1
fi

input="$1"
output="$2"

firtool --disable-annotation-unknown --parse-only "$input" \
    | circt-translate --export-firrtl --firrtl-version=2.0.0 --target-line-length=10000 -o "$output"

sed -i 's/FIRRTL version 2\.0\.0/FIRRTL version 1.2.0/' "$output"
sed -i 's/`//g' "$output"
