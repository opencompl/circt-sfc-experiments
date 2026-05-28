import sys
import os

config_base = lambda name: f"""
export DESIGN_NICKNAME = {name}
export DESIGN_NAME = {name}
export PLATFORM    = sky130hd

export VERILOG_FILES = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/{name}.v

export SYNTH_HDL_FRONTEND = slang

export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc

# No adders is better apparently
export ADDER_MAP_FILE :=

export CORE_UTILIZATION = 50
export PLACE_DENSITY_LB_ADDON = 0.25
export TNS_END_PERCENT = 100

export REMOVE_ABC_BUFFERS = 1

export CTS_CLUSTER_SIZE = 20
export CTS_CLUSTER_DIAMETER = 50

export SWAP_ARITH_OPERATORS = 1
export OPENROAD_HIERARCHICAL = 1
"""

if __name__ == "__main__":
    assert len(sys.argv) > 2, "Usage: gen_config.py <design_name> <path_to_output_directory>"

    out = sys.argv[2] + "/config.mk"

    # Check if a config already exists at that location
    if os.path.isfile(out):
        print("config file already exists at that location")
        exit(1)

    # create the config
    with open(out, 'w') as conf:
        conf.write(config_base(sys.argv[1]))

    print(f"Config created at {out}")
