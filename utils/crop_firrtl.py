import sys

# Removes all modules under a module called topModuleName
# and writes results to a given filename
def crop_file(filename: str, topModuleName: str, outputFile: str) -> None:
    lines = []
    # Read in file and close file asap as it might be huge
    with open(filename, "r") as f:
        lines: list[str] = f.readlines() # NOTE: This might explode if file is too large

    # get all the module lines in the file
    modules: list[str] = [m for m in lines if "module" in m]

    # find the chipTop line
    chiptop = next((m for m in modules if topModuleName in m), None)

    # Make sure we found chiptop
    assert chiptop is not None, f"Module {topModuleName} not found!"

    # our targeted end of file will be the line before the 
    # module that comes after chiptop, assuming no nested modules (otherwise fml)
    target_eof: int = lines.index(modules[modules.index(chiptop) + 1]) - 1

    # Crop our old lines list
    lines = lines[:target_eof]

    # Make sure we didn't just wipe our file
    assert len(lines) > 0, "Error: File was wiped!"

    # Write to a new file
    with open(outputFile, "w") as out_f:
        out_f.writelines(lines)

if __name__== "__main__":
    # Check that a file was given
    assert len(sys.argv) > 2, \
        "Usage: python crop_firrtl.py <chipyard_firrtl_file>.fir <topModuleName>"
    filename: str = sys.argv[1]
    top_name: str = sys.argv[2]

    # check filename format
    assert filename.split('.')[-1] == "fir", "input file must be a firrtl file"

    crop_file(filename, top_name, f"{filename.split('.')[0]}_cropped.fir")
