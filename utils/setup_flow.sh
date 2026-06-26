#!/usr/bin/env bash

PATH_TO_UTILS=utils
PATH_TO_TEMPLATES=$PATH_TO_UTILS/config_templates
PATH_TO_OPENROAD_DEST=OpenROAD-flow-scripts/flow/designs/sky130hd
TMP_DIR=$PWD/tmp

# Check arguments
if [ "$#" -lt 2 ]; then
  echo "Usage:"
  echo "  setup_flow.sh <design_name> <path_to_verilog_file>          # single .v (SFC)"
  echo "  setup_flow.sh <design_name> <path_to_filelist.f> [top] [clk]  # CIRCT split-verilog"
  echo ""
  echo "When the second argument ends in .f it is treated as a filelist and"
  echo "referenced in place; top defaults to ChipTop, clk to clock_uncore."
  exit 1
fi

TMP=$TMP_DIR/$1
DEST=$PATH_TO_OPENROAD_DEST/$1

# Detect filelist (CIRCT split-verilog) vs single-file (SFC) mode by extension.
case "$2" in
  *.f) MODE=filelist ;;
  *)   MODE=single ;;
esac

# Create a temp directory to build up the config
mkdir -p $TMP

if [ "$MODE" = "single" ]; then
    # Copy over the design file (if it exists)
    if [ -f "$2" ]; then
        cp -r $2 $TMP
    else
        echo "Verilog file $2 does not exist!"
        # cleanup
        rm -rf $TMP_DIR
        exit 1
    fi
else
    # Filelist mode: the .f is referenced in place, nothing to copy.
    if [ ! -f "$2" ]; then
        echo "Filelist $2 does not exist!"
        rm -rf $TMP_DIR
        exit 1
    fi
fi

# Check that we are running this from utils dir
if [ -d "$PATH_TO_TEMPLATES" ]; then
    cp $PATH_TO_TEMPLATES/* $TMP
else
    echo "config_templates not found!"
    # cleanup
    rm -rf $TMP_DIR
    exit 1
fi

# Generate the config file
if [ "$MODE" = "single" ]; then
    python $PATH_TO_UTILS/gen_config.py $1 $TMP
else
    TOP=${3:-ChipTop}
    CLOCK=${4:-clock_uncore}
    python $PATH_TO_UTILS/gen_config.py $1 $TMP \
        --filelist "$2" --top "$TOP" --clock "$CLOCK" --repo-root "$PWD"
fi

# Copy over all of the files to openroad (if it exists)
if [ -d "$PATH_TO_OPENROAD_DEST" ]; then
    # Check that the destination doesn't already exist
    if [ ! -d "$DEST" ]; then
       mkdir $DEST
       cp $TMP/* $DEST/
    else
        echo "Destination $DEST already exists!"
        rm -rf $TMP_DIR
        exit 1
    fi
else
    echo "OpenROAD-flow-scripts not found!"
    rm -rf $TMP_DIR
    exit 1
fi

# Delete the tmp
rm -rf $TMP_DIR

# Report
echo -e "Flow was successfully setup for $1 at:\n\t$PWD/$DEST"
