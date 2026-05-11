#!/usr/bin/env python3
import json
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <prefix>", file=sys.stderr)
    sys.exit(1)

PREFIX = sys.argv[1]

if " " in PREFIX:
    print(f"Error: prefix must not contain spaces.", file=sys.stderr)
    sys.exit(1)

FILES = [
    (f"{PREFIX}.anno.json.bak",          f"{PREFIX}.anno.json"),
    (f"{PREFIX}.appended.anno.json.bak", f"{PREFIX}.appended.anno.json"),
]

UNWANTED_CLASSES = [
    "chisel3.experimental.EnumAnnotations$EnumComponentAnnotation",
]

for backup, output in FILES:
    with open(backup) as f:
        annotations = json.load(f)

    filtered = [a for a in annotations if a.get("class") not in UNWANTED_CLASSES]

    removed = len(annotations) - len(filtered)
    print(f"{output}: removed {removed} annotations ({len(filtered)} remaining).")

    with open(output, "w") as f:
        json.dump(filtered, f, indent=2)


def strip_fir(backup, output):
    with open(backup) as f:
        text = f.read()

    # The annotation block in FIRRTL is delimited by %[[ ... ]]
    # The inner content is a JSON array (the %[[ contributes the opening [
    # and the ]] contributes the closing ]).
    prefix, rest = text.split("%[[", 1)
    json_raw, firrtl_body = rest.split("]]", 1)

    annotations = json.loads("[" + json_raw + "]")
    filtered = [a for a in annotations if a.get("class") not in UNWANTED_CLASSES]

    removed = len(annotations) - len(filtered)
    print(f"{output}: removed {removed} annotations ({len(filtered)} remaining).")

    json_inner = json.dumps(filtered, indent=2)[1:-1]  # strip outer [ and ]
    with open(output, "w") as f:
        f.write(prefix + "%[[" + json_inner + "]]" + firrtl_body)


strip_fir(f"{PREFIX}.fir.bak", f"{PREFIX}.fir")
