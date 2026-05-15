TARS := $(wildcard chipyard_tars/*.tar.gz)

.PHONY: untar clean
untar:
	mkdir -p chipyard_benchmarks
	@for tar in $(TARS); do \
		echo "Unpacking $$tar..."; \
		tar -xzf $$tar -C chipyard_benchmarks; \
	done

clean:
	rm -rf chipyard_benchmarks
