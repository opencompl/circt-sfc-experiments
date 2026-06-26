TARS := $(wildcard chipyard_tars/*.tar.gz)
ifdef BENCHMARK
BENCHMARK_NAMES := $(BENCHMARK)
else
BENCHMARK_NAMES := $(patsubst chipyard_tars/%.tar.gz,%,$(TARS))
endif
CHIPYARD_DIRS := $(addprefix benchmarks/chipyard/chipyard.harness.TestHarness.,$(BENCHMARK_NAMES))
CIRCT_DIRS := $(addprefix benchmarks/circt/chipyard.harness.TestHarness.,$(BENCHMARK_NAMES))
SFC_DIRS := $(addprefix benchmarks/sfc/chipyard.harness.TestHarness.,$(BENCHMARK_NAMES))

DESIGN_PLATFORM ?= sky130hd
OPENROAD_DESIGNS_DIR := OpenROAD-flow-scripts/flow/designs/$(DESIGN_PLATFORM)

.PHONY: all verilog openroad clean check-tools

check-tools:
	@utils/check_tools.sh

all: check-tools verilog

benchmarks/chipyard: $(CHIPYARD_DIRS)
benchmarks/circt: $(CIRCT_DIRS)
benchmarks/sfc: $(SFC_DIRS)

verilog: benchmarks/circt benchmarks/sfc
	@for dir in $(CIRCT_DIRS); do \
		bench_name=$$(basename "$$dir"); \
		find "$$dir" -name "$$bench_name.fir" | while read fir; do \
			echo "Running firtool on $$fir..."; \
			fir_dir=$$(dirname "$$fir"); \
			gen="$$fir_dir/gen-collateral"; \
			mkdir -p "$$gen"; \
			fir_dir_abs=$$(cd "$$fir_dir" && pwd); \
			anno_tmp=$$(mktemp --suffix=.json); \
			printf '[{"class":"sifive.enterprise.firrtl.MarkDUTAnnotation","target":"~TestHarness|ChipTop"},{"class":"sifive.enterprise.firrtl.ModuleHierarchyAnnotation","filename":"%s/top_module_hierarchy.json"}]' \
			    "$$fir_dir_abs" > "$$anno_tmp"; \
			lopts=""; \
			[ -f "$$fir_dir/.mfc_lowering_options" ] && lopts="--lowering-options=$$(cat "$$fir_dir/.mfc_lowering_options")"; \
			firtool --split-verilog --export-module-hierarchy -o "$$gen" $$lopts --annotation-file "$$anno_tmp" "$$fir"; \
			rm -f "$$anno_tmp"; \
			python3 utils/filter_chiptop_files.py \
			    "$$fir_dir/top_module_hierarchy.json" \
			    "$$gen" \
			    > "$${fir%.fir}.f"; \
		done; \
	done
	@for dir in $(SFC_DIRS); do \
		bench_name=$$(basename "$$dir"); \
		find "$$dir" -name "$$bench_name.fir" | while read fir; do \
			echo "Running firrtl on $$fir..."; \
			fir_dir=$$(dirname "$$fir"); \
			gen="$$fir_dir/gen-collateral"; \
			mkdir -p "$$gen"; \
			if firrtl -i "$$fir" -td "$$gen" -e verilog; then \
				python3 utils/filter_reachable_modules.py "$$gen" ChipTop > "$${fir%.fir}.f"; \
			else \
				echo "Warning: SFC firrtl failed on $$bench_name, skipping ChipTop filelist"; \
			fi; \
		done; \
	done

benchmarks/chipyard/chipyard.harness.TestHarness.%: chipyard_tars/%.tar.gz
	mkdir -p benchmarks/chipyard
	tar -xzf $< -C benchmarks/chipyard

benchmarks/circt/chipyard.harness.TestHarness.%: benchmarks/chipyard/chipyard.harness.TestHarness.%
	mkdir -p benchmarks/circt
	cp -r $< $@
	@find $@ -name "*.anno.json" | while read f; do mv "$$f" "$$f.bak"; done
	@find $@ -name "*.fir" | while read f; do mv "$$f" "$$f.bak"; done
	@find $@ -name "*.fir.bak" | while read fir_bak; do \
		prefix="$${fir_bak%.fir.bak}"; \
		if [ -f "$$prefix.anno.json.bak" ]; then \
			echo "Running strip_annotations.py on $$prefix..."; \
			python3 utils/strip_annotations.py "$$prefix"; \
		else \
			echo "Skipping strip_annotations.py on $$prefix (no anno.json), restoring fir..."; \
			mv "$$fir_bak" "$$prefix.fir"; \
		fi; \
	done

benchmarks/sfc/chipyard.harness.TestHarness.%: benchmarks/circt/chipyard.harness.TestHarness.%
	mkdir -p benchmarks/sfc
	cp -r $< $@
	@find $@ -name "chipyard.harness.TestHarness.$*.fir" | while read f; do \
		echo "Converting $$f..."; \
		tmp=$$(mktemp); \
		utils/convert_firrtl_2_to_1.sh "$$f" "$$tmp" && mv "$$tmp" "$$f"; \
	done

# Generate an OpenROAD-flow-scripts design (config.mk + constraint.sdc) for each
# CIRCT benchmark, consuming the per-benchmark filelist produced by `verilog`.
# Run `make verilog` (or `make`) first so the .f files exist.
openroad:
	@for name in $(BENCHMARK_NAMES); do \
		f="benchmarks/circt/chipyard.harness.TestHarness.$$name/chipyard.harness.TestHarness.$$name.f"; \
		if [ ! -s "$$f" ]; then \
			echo "Skipping $$name: no filelist at $$f (run 'make verilog' first)"; \
			continue; \
		fi; \
		if [ -d "$(OPENROAD_DESIGNS_DIR)/$$name" ]; then \
			echo "Skipping $$name: design already exists at $(OPENROAD_DESIGNS_DIR)/$$name"; \
			continue; \
		fi; \
		echo "Setting up OpenROAD flow for $$name..."; \
		utils/setup_flow.sh "$$name" "$$f"; \
	done

clean:
	rm -rf benchmarks
