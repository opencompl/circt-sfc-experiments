#!/usr/bin/env python3
import json, sys, pathlib

hier_file = pathlib.Path(sys.argv[1])
gen_dir   = pathlib.Path(sys.argv[2])

with open(hier_file) as f:
    hier = json.load(f)

def collect_modules(node, seen=None):
    if seen is None:
        seen = set()
    name = node.get("module_name")
    if name:
        seen.add(name)
    for child in node.get("instances", []):
        collect_modules(child, seen)
    return seen

modules = collect_modules(hier)

for ext in ("*.sv", "*.v"):
    for src in sorted(gen_dir.glob(ext)):
        if src.stem in modules:
            print(src)

bench_dir = hier_file.parent
for mems in sorted(bench_dir.glob("*.top.mems.v")):
    print(mems)
