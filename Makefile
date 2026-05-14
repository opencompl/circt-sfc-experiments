ZIPS := $(wildcard chipyard_zips/*.zip)

.PHONY: unzip
unzip:
	@for zip in $(ZIPS); do \
		echo "Unzipping $$zip..."; \
		unzip -o $$zip; \
	done
