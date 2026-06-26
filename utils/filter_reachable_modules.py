#!/usr/bin/env python3
# Emit a filelist of the Verilog/SystemVerilog modules reachable from a given
# top module, by walking module instantiations in the *emitted* sources.
#
# Used for the SFC path: the Scala FIRRTL Compiler emits every module in the
# circuit regardless of the circuit's main module, and its post-dedup module
# names diverge from firtool's, so neither re-rooting nor reusing firtool's
# top_module_hierarchy.json gives a correct ChipTop-only filelist. Walking the
# instantiation graph over SFC's own emitted output uses SFC's own names and
# correctly drops the TestHarness/sim wrapper.
import re, sys, pathlib, collections

gen = pathlib.Path(sys.argv[1])
top = sys.argv[2] if len(sys.argv) > 2 else "ChipTop"

files = {p.stem: p for p in sorted(gen.glob("*.v")) + sorted(gen.glob("*.sv"))}

# Matches an instantiation line like "  ModuleName instName (".
# The "module name in files" guard below filters out keyword false-positives.
inst_re = re.compile(r'^\s*([A-Za-z_]\w*)\s+\w+\s*\(')

children = collections.defaultdict(set)
for name, p in files.items():
    for ln in p.read_text().splitlines():
        m = inst_re.match(ln)
        if m and m.group(1) in files and m.group(1) != name:
            children[name].add(m.group(1))

seen = set()
stack = [top]
while stack:
    n = stack.pop()
    if n in seen or n not in files:
        continue
    seen.add(n)
    stack.extend(children.get(n, ()))

for name in sorted(seen):
    print(files[name])
