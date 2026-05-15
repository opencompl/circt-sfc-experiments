ZIPS := $(wildcard chipyard_zips/*.zip)

.PHONY: unzip clean
unzip:
	@for zip in $(ZIPS); do \
		echo "Unzipping $$zip..."; \
		unzip -o $$zip -d chipyard_benchmarks; \
	done

clean:
	rm -rf chipyard_benchmarks
