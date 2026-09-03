import sys

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

    # get all the module lines in the file
    modules: list[str] = [m for m in lines if "module" in m]

    # find the chipTop line
    chiptop = next((m for m in modules if topModuleName in m), None)

    # Make sure we found chiptop
    assert chiptop is not None, f"Module {topModuleName} not found!"

    # find which module comes after chiptop
    nextModuleIndex: int = modules.index(chiptop) + 1

    # Make sure such a module exists
    assert len(modules) > nextModuleIndex, "No modules after ChipTop to crop!"

    # our targeted end of file will be the line before the 
    # module that comes after chiptop, assuming no nested modules (otherwise fml)
    target_eof: int = lines.index(modules[nextModuleIndex]) - 1

    # Crop our old lines list
    lines = lines[:target_eof]

    # Find and rename the circuit annotation to match the top module
    circuit_anno: str = next((c for c in lines if "circuit" in c), "")
    assert circuit_anno != "", "Missing circuit annotation"

    new_circuit_anno: str = rename_circuit(topModuleName, circuit_anno)

    # Check that our circuit annotation is well in our file
    circuit_anno_idx = lines.index(circuit_anno)
    assert len(lines) > circuit_anno_idx, "Circuit annotation was found out of bounds!"

    # Update our circuit annotation 
    lines[lines.index(circuit_anno)] = new_circuit_anno

    # Make sure we didn't just wipe our file
    assert len(lines) > 0, "Error: File was wiped!"

    # Write to a new file
    with open(outputFile, "w") as out_f:
        out_f.writelines(lines)

    print(f"Cropped result stored in {outputFile}")

if __name__== "__main__":
    # Check that a file was given
    assert len(sys.argv) > 2, \
        "Usage: python crop_firrtl.py <chipyard_firrtl_file>.fir <topModuleName>"
    filename: str = sys.argv[1]
    top_name: str = sys.argv[2]

    # check filename format
    assert filename.split('.')[-1] == "fir", "input file must be a firrtl file"

    crop_file(filename, top_name, f"{'.'.join(filename.split('.')[:-1])}_cropped.fir")
