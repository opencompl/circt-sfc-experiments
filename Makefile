TARS := $(wildcard chipyard_tars/*.tar.gz)
BENCHMARK_NAMES := $(patsubst chipyard_tars/%.tar.gz,%,$(TARS))
CHIPYARD_DIRS := $(addprefix benchmarks/chipyard/chipyard.harness.TestHarness.,$(BENCHMARK_NAMES))
CIRCT_DIRS := $(addprefix benchmarks/circt/chipyard.harness.TestHarness.,$(BENCHMARK_NAMES))
SFC_DIRS := $(addprefix benchmarks/sfc/chipyard.harness.TestHarness.,$(BENCHMARK_NAMES))

.PHONY: all verilog clean

all: verilog

benchmarks/chipyard: $(CHIPYARD_DIRS)
benchmarks/circt: $(CIRCT_DIRS)
benchmarks/sfc: $(SFC_DIRS)

verilog: benchmarks/circt benchmarks/sfc
	@find benchmarks/circt -name "*.fir" | while read fir; do \
		echo "Running firtool on $$fir..."; \
		firtool "$$fir" -o "$${fir%.fir}.sv"; \
	done
	@find benchmarks/sfc -name "*.fir" | while read fir; do \
		echo "Running firrtl on $$fir..."; \
		firrtl -i "$$fir" -o "$${fir%.fir}.v" -X verilog; \
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
		echo "Running strip_annotations.py on $$prefix..."; \
		python3 utils/strip_annotations.py "$$prefix"; \
	done

benchmarks/sfc/chipyard.harness.TestHarness.%: benchmarks/circt/chipyard.harness.TestHarness.%
	mkdir -p benchmarks/sfc
	cp -r $< $@
	@find $@ -name "*.fir" | while read f; do \
		echo "Converting $$f..."; \
		tmp=$$(mktemp); \
		utils/convert_firrtl_2_to_1.sh "$$f" "$$tmp" && mv "$$tmp" "$$f"; \
	done

clean:
	rm -rf benchmarks
