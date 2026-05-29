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

constraint_base = lambda name: f"""
current_design {name}

set clk_name core_clock
set clk_port_name clk_i
set clk_period 10.0
set clk_io_pct 0.2

set clk_port [get_ports $clk_port_name]

create_clock -name $clk_name -period $clk_period $clk_port

set non_clock_inputs [all_inputs -no_clocks]

set_input_delay [expr $clk_period * $clk_io_pct] -clock $clk_name $non_clock_inputs
set_output_delay [expr $clk_period * $clk_io_pct] -clock $clk_name [all_outputs]
"""

if __name__ == "__main__":
    assert len(sys.argv) > 2, "Usage: gen_config.py <design_name> <path_to_output_directory>"
    
    # Check that the given path is valid
    if not os.path.isdir(sys.argv[2]):
        print(f"{sys.argv[2]} is not a valid directory!")
        exit(1)

    # Output paths
    out_config = sys.argv[2] + "/config.mk"
    out_const = sys.argv[2] + "/constraint.sdc"

    # Check if one of the files already exists at that location
    if os.path.isfile(out_config):
        print("config file already exists at that location")
        exit(1)

    if os.path.isfile(out_const):
        print("constraint file already exists at that location")
        exit(1)

    # create the files
    with open(out_config, 'w') as conf:
        conf.write(config_base(sys.argv[1]))
    
    with open(out_const, 'w') as constr:
        constr.write(constraint_base(sys.argv[1]))

    print(f"Files created at:\n\t{out_config}\n\t{out_const}")

