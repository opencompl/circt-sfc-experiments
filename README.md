# SFC vs. CIRCT FIRRTL compilation benchmarking (WIP)

- Run `make verilog` to generate a benchmark directory containing Verilog generated from the supported Chipyard benchmarks by both Firtool and SFC.  
- Run `make openroad-config` to setup the OpenroadFlowScripts.  
- Finally, run `make openroad` to synthesize all designs, or for a single design:  
```sh
cd OpenROAD-flow-scripts/flow  
make DESIGN_CONFIG=./designs/sky130hd/<DESIGN_NAME>/config.mk  
make DESIGN_CONFIG=./designs/sky130hd/<DESIGN_NAME>/config.mk gui_final
```
Where `DESIGN_NAME` is one of: `GemminiRocketConfig`, `LargeBoomV4Config`, `MediumBoomV4Config`, `MegaBoomV4Config`, or `SmallBoomV4Config`.

## Requirements
- [firrtl2 v6.0.0](https://github.com/ucb-bar/firrtl2/releases)
- A recent CIRCT build with: [`firtool`,  `circt-translate`](https://github.com/llvm/circt/releases)
- Recent verisons of [`yosys`, `openroad`, `klayout`, (all part of the oss-cad-suite)](https://github.com/YosysHQ/oss-cad-suite-build/releases)
- Basic things like Python3 and GNU-make

## TODO
- All designs crash on ABC after a few hours... [#6](https://github.com/opencompl/circt-sfc-experiments/issues/6)
- Integrate SFC designs with openroad flow.

## Integrating OpenROAD  
> NOTE: The entire openroad config setup can be run using `make openroad-config`.

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
make DESIGN_CONFIG=./designs/sky130hd/<DESIGN_NAME>/config.mk  
make DESIGN_CONFIG=./designs/sky130hd/<DESIGN_NAME>/config.mk gui_final
```  
Then in the tcl command box, run commands to get the QoR reports:  
```tcl  
report_design_area  
report_power  
report_wns
report_tns
report_worst_slack
```  
> NOTE: The entire openroad process for all designs can be launched using `make openroad`.

Note: 
- Chipyard benchmarks are generated from [this branch on my fork](https://github.com/TaoBi22/chipyard/tree/eval-configs).
- OpenRoadFlowScripts can be found on [this branch of our other fork](https://github.com/dobios/OpenROAD-flow-scripts/tree/372d225d5fd8232f255c4bbcfece19a1ff7b12bd)
