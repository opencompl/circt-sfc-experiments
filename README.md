# SFC vs. CIRCT FIRRTL compilation benchmarking (WIP)

Run `make` to generate a benchmark directory containing Verilog generated from the supported Chipyard benchmarks by both Firtool and SFC.

TODO:
- Small BOOM seems to need a higher character limit in FIRRTL version conversion
- Large BOOM errors out on Firtool  

## Integrating OpenROAD  

For the openroad integration, we rely on OpenROAD-flow-scripts.  
To add a new design, you need to create a folder under `OpenROAD-flow-scripts/flow/designs/$(DESIGN_PLATFORM)` with the name of your design and fill it with the following:

```sh
BUILD # generic is reused verbatim for every design  
config.mk # specific to design, must be regenerated  
constraint.sdc # used for autotuning, must be generated (currently suboptimal)  
autotuner.json # autotuning params, can be left as is  
$(DESIGN_NAME).v # the actual design file  
```  
  
For example, the files needed to run a simple fifo design can be found [here](./example/fifo). 
To run the example copy the files into the sky130hd folder:  
```sh  
cp -r example/fifo OpenROAD-flow-scripts/flow/design/sky130hd  
```  
  
> NOTE: The entire process up until this point is automated using the [setup script](./utils/setup_flow.sh).  
  
Before running openroad-flow-scripts make sure you tell it where your yosys and openroad binaries are:  
```sh
export OPENROAD_EXE=$(command -v openroad)
export YOSYS_EXE=$(command -v yosys)
```

You can then run the flow for your design using:  
```sh  
cd OpenROAD-flow-scripts/flow  
make DESIGN_CONFIG=./designs/sky130hd/fifo/config.mk  
make DESIGN_CONFIG=./designs/sky130hd/fifo/config.mk gui_final
```  
Then in the tcl command box, run commands to get the QoR reports:  
```tcl  
report_design_area  
report_power  
report_wns
report_tns
report_worst_slack
```  

