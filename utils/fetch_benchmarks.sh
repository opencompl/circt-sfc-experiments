#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if the user provided an input directory
if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_directory>"
    echo "Example: $0 ../my_directories_to_archive"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="chipyard_tars"

# Define the list of supported benchmarks here
SUPPORTED_BENCHMARKS=(
    "GemminiRocketConfig"
    "LargeBoomV4Config"
    "MediumBoomV4Config"
    "MegaBoomV4Config"
    "SmallBoomV4Config"
)

# Check if the provided input is a valid directory
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Directory '$INPUT_DIR' does not exist."
    exit 1
fi

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Looking for supported benchmarks in '$INPUT_DIR'..."
echo "Outputting tarballs to '$OUTPUT_DIR/'..."
echo "------------------------------------------------"

PREFIX="chipyard.harness.TestHarness."

# Iterate over the supported benchmarks list
for DIR_NAME in "${SUPPORTED_BENCHMARKS[@]}"; do
    FULL_DIR_NAME="${PREFIX}${DIR_NAME}"
    target_dir="$INPUT_DIR/$FULL_DIR_NAME"
    
    # Check if the supported benchmark directory actually exists in the input folder
    if [ -d "$target_dir" ]; then
        ARCHIVE_NAME="${OUTPUT_DIR}/${DIR_NAME}.tar.gz"
        
        echo "Archiving '$FULL_DIR_NAME' -> '$ARCHIVE_NAME'..."
        
        # -c: create, -z: gzip, -f: file
        # -C changes the working directory to INPUT_DIR before archiving, 
        # so the tarball inner structure is clean (just the dir, not the full path)
        tar -czf "$ARCHIVE_NAME" -C "$INPUT_DIR" "$FULL_DIR_NAME"
    else
        echo "Warning: Target folder '$FULL_DIR_NAME' not found in '$INPUT_DIR'. Skipping."
    fi
done

echo "------------------------------------------------"
echo "Done! Available benchmarks have been archived in '$OUTPUT_DIR'."