#!/usr/bin/env python3
# Emit a blackbox-only annotation file for the cropped SFC circuit.
#
# SFC writes extmodule bodies itself from BlackBoxInlineAnno (firrtl -faf), which
# keeps the SFC path independent of firtool. The full anno file cannot be used as
# is: it carries firtool-era classes SFC has no constructor for, and DontTouch
# targets the crop deleted. Keep only the blackboxes this circuit instantiates,
# re-rooted at the cropped top, so the sim-only ones (ClockSourceAtFreqMHz, Sim*)
# are never written and cannot reach Yosys.
import json, re, sys

annos, fir, old_top, new_top = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

wanted = {f"{m.group(1)}.v" for m in
          (re.match(r"\s*defname\s*=\s*(\S+)", line) for line in open(fir)) if m}

keep = []
for a in json.load(open(annos)):
    if not a.get("class", "").endswith("BlackBoxInlineAnno"):
        continue
    if a.get("name") not in wanted:
        continue
    target = a.get("target")
    if isinstance(target, str) and target.startswith(old_top + "."):
        a["target"] = new_top + target[len(old_top):]
    keep.append(a)

found = {a["name"] for a in keep}
missing = sorted(wanted - found)
if missing:
    sys.exit(f"{annos}: no BlackBoxInlineAnno provides {missing}")

json.dump(keep, sys.stdout, indent=1)
