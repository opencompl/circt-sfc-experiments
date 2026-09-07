import json
import re
import sys

# A FIRRTL module declaration, e.g. "  public module ChipTop :"
MODULE_RE = re.compile(r'^\s*(?:public\s+)?(?:module|extmodule|intmodule)\s+(\w+)\s*:')

# Get line index of circuit declaration
def find_circuit(lines: list[str]) -> int:
    idx = next((i for i, l in enumerate(lines) if l.startswith("circuit")), -1)
    assert idx >= 0, "Missing circuit annotation"
    return idx

# Get line index of the end of an annotation on a circuit declaration (returns circuit line index if there is no anno)
def annotation_end(lines: list[str], circuit_idx: int) -> int:
    if "%[[" not in lines[circuit_idx]:
        return circuit_idx

    # Single-line
    if lines[circuit_idx].rstrip().endswith("]]"):
        return circuit_idx

    # Multi-line
    end = next((i for i in range(circuit_idx + 1, len(lines))
                if lines[i].strip() == "]]"), -1)
    assert end >= 0, "Unterminated inline annotation blob"
    return end

# All module declarations in the file as (line index, module name)
def find_modules(lines: list[str], start: int) -> list[tuple[int, str]]:
    matches = ((i, MODULE_RE.match(lines[i])) for i in range(start, len(lines)))
    return [(i, m.group(1)) for i, m in matches if m is not None]


# Annotation classes that are safe to drop when their target is removed
DROPPABLE = ("DedupGroupAnnotation", "BlackBoxInlineAnno")

# The module a target names, or None when it names the circuit itself
def target_module(target: str) -> str | None:
    if target.startswith('~'):
        body: str = target[1:]
        if '|' not in body:
            return None
        return re.split(r'[/>]', body.split('|', 1)[1])[0]

    # Legacy Circuit.Module form
    parts: list[str] = target.split('.')
    return parts[1] if len(parts) > 1 else None

# Returns the given annotation target updated to use the new top module
def reroot_target(target: str, newTop: str) -> str:
    if target.startswith('~'):
        body: str = target[1:]
        if '|' not in body:
            return f"~{newTop}"
        return f"~{newTop}|{body.split('|', 1)[1]}"

    return '.'.join([newTop] + target.split('.')[1:])

# Get the inline annotation array carried by the circuit declaration
def read_annos(lines: list[str], circuit_idx: int, anno_end: int) -> list[dict]:
    blob: str = (lines[circuit_idx].partition('%')[2]
                 + ''.join(lines[circuit_idx + 1:anno_end + 1])).strip()
    assert blob.startswith('[[') and blob.endswith(']]'), \
        "Malformed inline annotations"
    return json.loads(blob[1:-1])

# Update surviving annotations to have the right root (the new top module and drop the ones whose target the crop removed
def crop_annos(annos: list[dict], survivors: set[str], topModuleName: str) \
        -> list[dict]:
    keep: list[dict] = []
    for a in annos:
        target: str | None = a.get("target")

        # Targetless annotations apply to the whole circuit
        if target is None:
            keep.append(a)
            continue

        module: str | None = target_module(target)
        if module is not None and module not in survivors:
            assert a.get("class", "").endswith(DROPPABLE), \
                f"Crop removed {module}, target of a {a.get('class')}"
            continue

        a["target"] = reroot_target(target, topModuleName)
        keep.append(a)

    return keep

# The circuit declaration lines for a cropped circuit, carrying its annotations
def circuit_lines(head: str, annos: list[dict]) -> list[str]:
    if not annos:
        return [head + "\n"]

    body: list[str] = json.dumps(annos, indent=1).splitlines()
    return [f"{head}%[{body[0]}\n"] \
        + [l + "\n" for l in body[1:-1]] \
        + [f"{body[-1]}]\n"]

# Rename a given circuit annotation using a given topModuleName
# Skips if the topModuleName is already the circuit name
# Returns the renamed circuit annotation.
def rename_circuit(topModuleName: str, circuit_anno: str) -> str:
    # Extract the current top_module name
    tokenize_anno: list[str] = circuit_anno.split(' ')
    top_name_idx: int = tokenize_anno.index('circuit') + 1

    # Sanity check, our circuit annotation is well formed
    assert len(tokenize_anno) > top_name_idx, "Malformed circuit annotation"

    # Extract the name and check if it needs to be changed
    name: str = tokenize_anno[top_name_idx]
    if name == topModuleName:
        return circuit_anno

    # Update the annotation since the name is changing
    tokenize_anno[top_name_idx] = topModuleName

    return ' '.join(tokenize_anno)

# Removes all modules under a module called topModuleName
# and writes results to a given filename
def crop_file(filename: str, topModuleName: str, outputFile: str) -> None:
    print(f"Cropping {filename} after module {topModuleName}...")
    lines: list[str] = []
    # Read in file and close file asap as it might be huge
    with open(filename, "r") as f:
        lines = f.readlines() # NOTE: This might explode if file is too large

    # get all the module declarations, skipping any inline annotations
    circuit_idx: int = find_circuit(lines)
    anno_end: int = annotation_end(lines, circuit_idx)
    modules: list[tuple[int, str]] = find_modules(lines, anno_end + 1)

    # find the chipTop declaration
    chiptop = next((i for i, (_, name) in enumerate(modules)
                    if name == topModuleName), None)

    # Make sure we found chiptop
    assert chiptop is not None, f"Module {topModuleName} not found!"

    # find which module comes after chiptop
    nextModuleIndex: int = chiptop + 1

    # Make sure such a module exists
    assert len(modules) > nextModuleIndex, "No modules after ChipTop to crop!"

    # our targeted end of file will be the line before the 
    # module that comes after chiptop, assuming no nested modules (otherwise fml)
    target_eof: int = modules[nextModuleIndex][0] - 1

    # the modules up to and including chiptop are the ones the crop keeps
    survivors: set[str] = {name for _, name in modules[:nextModuleIndex]}

    # Read the inline annotations before the crop shifts anything
    annos: list[dict] = read_annos(lines, circuit_idx, anno_end) \
        if '%[' in lines[circuit_idx] else []

    # Crop our old lines list
    lines = lines[:target_eof]

    # Rename the circuit annotation to match the top module, and re-root the
    # annotations it carries so their targets still resolve
    head: str = rename_circuit(topModuleName,
                               lines[circuit_idx].partition('%')[0].rstrip('\n'))
    lines[circuit_idx:anno_end + 1] = \
        circuit_lines(head, crop_annos(annos, survivors, topModuleName))

    # Make sure we didn't just wipe our file
    assert len(lines) > 0, "Error: File was wiped!"

    # Write to a new file
    with open(outputFile, "w") as out_f:
        out_f.writelines(lines)

    print(f"Cropped result stored in {outputFile}")

if __name__== "__main__":
    # Check that a file was given
    assert len(sys.argv) > 2, \
        "Usage: python crop_firrtl.py <chipyard_firrtl_file>.fir <topModuleName> [inplace=0, 1]?"
    filename: str = sys.argv[1]
    top_name: str = sys.argv[2]
    inplace: bool = False

    if len(sys.argv) > 3:
        inplace = bool(int(sys.argv[3]))

    # check filename format
    assert filename.split('.')[-1] == "fir", "input file must be a firrtl file"

    crop_file( \
        filename, top_name,  \
        filename if inplace else f"{'.'.join(filename.split('.')[:-1])}_cropped.fir" \
    ) 
