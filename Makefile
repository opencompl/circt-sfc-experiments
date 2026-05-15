TARS := $(wildcard chipyard_tars/*.tar.gz)
BENCHMARK_DIRS := $(wildcard benchmarks/chipyard/*)
CIRCT_BENCHMARK_DIRS := $(patsubst benchmarks/chipyard/%,benchmarks/circt/%,$(BENCHMARK_DIRS))
SFC_BENCHMARK_DIRS := $(patsubst benchmarks/chipyard/%,benchmarks/sfc/%,$(BENCHMARK_DIRS))

.PHONY: untar clean all
all:
	$(MAKE) untar
	$(MAKE) benchmarks/circt
	$(MAKE) benchmarks/sfc

untar:
	mkdir -p benchmarks/chipyard
	@for tar in $(TARS); do \
		echo "Unpacking $$tar..."; \
		tar -xzf $$tar -C benchmarks/chipyard; \
	done

benchmarks/circt: $(CIRCT_BENCHMARK_DIRS)

benchmarks/circt/%: benchmarks/chipyard/%
	mkdir -p benchmarks/circt
	cp -r $< $@
	@find $@ -name "*.anno.json" | while read f; do mv "$$f" "$$f.bak"; done
	@find $@ -name "*.fir" | while read f; do mv "$$f" "$$f.bak"; done
	@find $@ -name "*.fir.bak" | while read fir_bak; do \
		prefix="$${fir_bak%.fir.bak}"; \
		echo "Running strip_annotations.py on $$prefix..."; \
		python3 utils/strip_annotations.py "$$prefix"; \
	done

benchmarks/sfc: $(SFC_BENCHMARK_DIRS)

benchmarks/sfc/%: benchmarks/circt/%
	mkdir -p benchmarks/sfc
	cp -r $< $@
	@find $@ -name "*.fir" | while read f; do \
		echo "Converting $$f..."; \
		tmp=$$(mktemp); \
		utils/convert_firrtl_2_to_1.sh "$$f" "$$tmp" && mv "$$tmp" "$$f"; \
	done

clean:
	rm -rf benchmarks
