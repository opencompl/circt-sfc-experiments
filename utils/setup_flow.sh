#!/usr/bin/env bash

PATH_TO_UTILS=utils
PATH_TO_TEMPLATES=$PATH_TO_UTILS/config_templates
PATH_TO_OPENROAD_DEST=OpenROAD-flow-scripts/flow/designs/sky130hd

# Check arguments  
if [ "$#" -lt 2 ]; then
  echo "Usage: setup_flow.sh <design_name> <path_to_verilog_file>"
  exit 1
fi

TMP=$PWD/tmp/$1
DEST=$PATH_TO_OPENROAD_DEST/$1

# Create a temp directory to build up the config  
mkdir -p $TMP  

# Copy over the design file (if it exists)
if [ -f "$2" ]; then
    cp -r $2 $TMP/
else
    echo "Verilog file $1 does not exist!"
    # cleanup 
    rm -rf $TMP
    exit 1
fi

# Check that we are running this from utils dir
if [ -d "$PATH_TO_TEMPLATES" ]; then
    cp $PATH_TO_TEMPLATES/* $TMP/
else 
    echo "config_templates not found!"
    # cleanup
    rm -rf $TMP
    exit 1
fi

# Generate the config file
python $PATH_TO_UTILS/gen_config.py $1 $TMP

# Copy over all of the files to openroad (if it exists)
if [ -d "$PATH_TO_OPENROAD_DEST" ]; then 
    # Check that the destination doesn't already exist
    if [ ! -d "$DEST" ]; then
       mkdir $DEST
       cp $TMP/* $DEST/
    else
        echo "Destination $DEST already exists!"
        rm -rf $TMP
        exit 1
    fi
else
    echo "OpenROAD-flow-scripts not found!"
    rm -rf $TMP
    exit 1
fi

# Delete the tmp
rm -rf $TMP

# Report
echo "Flow was successfully setup for $1 at $DEST"

