TARS := $(wildcard chipyard_tars/*.tar.gz)
BENCHMARK_DIRS := $(wildcard chipyard_benchmarks/*)
CIRCT_BENCHMARK_DIRS := $(patsubst chipyard_benchmarks/%,circt_benchmarks/%,$(BENCHMARK_DIRS))
SFC_BENCHMARK_DIRS := $(patsubst chipyard_benchmarks/%,sfc_benchmarks/%,$(BENCHMARK_DIRS))

.PHONY: untar clean circt_benchmarks sfc_benchmarks
untar:
	mkdir -p chipyard_benchmarks
	@for tar in $(TARS); do \
		echo "Unpacking $$tar..."; \
		tar -xzf $$tar -C chipyard_benchmarks; \
	done

circt_benchmarks: $(CIRCT_BENCHMARK_DIRS)

circt_benchmarks/%: chipyard_benchmarks/%
	mkdir -p circt_benchmarks
	cp -r $< $@
	@find $@ -name "*.anno.json" | while read f; do mv "$$f" "$$f.bak"; done
	@find $@ -name "*.fir" | while read f; do mv "$$f" "$$f.bak"; done
	@find $@ -name "*.fir.bak" | while read fir_bak; do \
		prefix="$${fir_bak%.fir.bak}"; \
		echo "Running strip_annotations.py on $$prefix..."; \
		python3 utils/strip_annotations.py "$$prefix"; \
	done

sfc_benchmarks: $(SFC_BENCHMARK_DIRS)

sfc_benchmarks/%: circt_benchmarks/%
	mkdir -p sfc_benchmarks
	cp -r $< $@
	@find $@ -name "*.fir" | while read f; do \
		echo "Converting $$f..."; \
		tmp=$$(mktemp); \
		utils/convert_firrtl_2_to_1.sh "$$f" "$$tmp" && mv "$$tmp" "$$f"; \
	done

clean:
	rm -rf chipyard_benchmarks circt_benchmarks sfc_benchmarks
