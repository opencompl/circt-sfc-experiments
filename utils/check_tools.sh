#!/usr/bin/env bash
set -euo pipefail

ok=true

for tool in firrtl firtool circt-translate; do
    if ! command -v "$tool" &>/dev/null; then
        echo "ERROR: $tool not found in PATH" >&2
        ok=false
    fi
done

$ok || exit 1

for tool in firtool circt-translate; do
    version=$("$tool" --version 2>&1)
    if echo "$version" | grep -qi "debug"; then
        echo "WARNING: $tool --version output contains 'debug' — debug builds may take an excessive amount of time to process larger benchmarks" >&2
    fi
done
