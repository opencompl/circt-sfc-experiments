import argparse
import os

# Shared OpenROAD/ORFS knobs, kept identical between single-file and filelist
# modes so the only thing that changes is how VERILOG_FILES is populated.
config_common = """
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

# Single monolithic Verilog file (SFC-style output): one .v copied into the
# design directory and named after the design nickname.
config_single = lambda nickname, top: f"""
export DESIGN_NICKNAME = {nickname}
export DESIGN_NAME = {top}
export PLATFORM    = sky130hd

export VERILOG_FILES = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/{nickname}.v
{config_common}"""

# CIRCT (firtool) split-verilog output: many .sv files plus a few blackbox .v
# cells. The top-level Makefile generates a per-benchmark filelist (<bench>.f)
# scoped to the DUT hierarchy via filter_chiptop_files.py. We consume that
# filelist in place so firtool re-runs stay the single source of truth. Paths in
# the .f are relative to the repo root, so we re-anchor them.
config_filelist = lambda nickname, top, repo_root, filelist: f"""
export DESIGN_NICKNAME = {nickname}
export DESIGN_NAME = {top}
export PLATFORM    = sky130hd

REPO_ROOT := {repo_root}
FILELIST  := {filelist}

export VERILOG_FILES = $(addprefix $(REPO_ROOT)/,$(shell cat $(FILELIST)))
{config_common}"""

constraint_base = lambda top, clock: f"""
current_design {top}

set clk_name core_clock
set clk_port_name {clock}
set clk_period 10.0
set clk_io_pct 0.2

set clk_port [get_ports $clk_port_name]

create_clock -name $clk_name -period $clk_period $clk_port

set non_clock_inputs [all_inputs -no_clocks]

set_input_delay [expr $clk_period * $clk_io_pct] -clock $clk_name $non_clock_inputs
set_output_delay [expr $clk_period * $clk_io_pct] -clock $clk_name [all_outputs]
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate an ORFS config.mk + constraint.sdc for a design.")
    parser.add_argument("nickname", help="design nickname (output/results dir)")
    parser.add_argument("out_dir", help="directory to write config.mk/constraint.sdc")
    parser.add_argument("--filelist",
                        help="path to a CIRCT split-verilog filelist (.f); "
                             "when given, VERILOG_FILES reads it in place")
    parser.add_argument("--top",
                        help="top module / DESIGN_NAME (default: nickname)")
    parser.add_argument("--clock", default="clk_i",
                        help="clock port name for the SDC (default: clk_i)")
    parser.add_argument("--repo-root", default=os.getcwd(),
                        help="root the filelist paths are relative to "
                             "(default: current dir)")
    args = parser.parse_args()

    # Check that the given path is valid
    if not os.path.isdir(args.out_dir):
        print(f"{args.out_dir} is not a valid directory!")
        exit(1)

    top = args.top if args.top else args.nickname

    # Output paths
    out_config = os.path.join(args.out_dir, "config.mk")
    out_const = os.path.join(args.out_dir, "constraint.sdc")

    # Check if one of the files already exists at that location
    if os.path.isfile(out_config):
        print("config file already exists at that location")
        exit(1)

    if os.path.isfile(out_const):
        print("constraint file already exists at that location")
        exit(1)

    if args.filelist:
        config = config_filelist(args.nickname, top,
                                 os.path.abspath(args.repo_root),
                                 os.path.abspath(args.filelist))
    else:
        config = config_single(args.nickname, top)

    # create the files
    with open(out_config, 'w') as conf:
        conf.write(config)

    with open(out_const, 'w') as constr:
        constr.write(constraint_base(top, args.clock))

    print(f"Files created at:\n\t{out_config}\n\t{out_const}")
