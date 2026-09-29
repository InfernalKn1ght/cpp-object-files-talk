PY ?= python3
RUNS ?= 10
L ?= all
M ?= O0g

.PHONY: all build metrics report demo cabi repro slides clean distclean

all: metrics report cabi repro

build:            ## build .o files for all languages/modes
	$(PY) scripts/collect.py --build-only

metrics:          ## build .o files, measure compilation, parse ELF -> results/*.csv
	$(PY) scripts/collect.py --runs $(RUNS)

report:           ## generate tables, sizes.csv, and charts from results/*.csv
	$(PY) scripts/report.py

demo:             ## live demo: make demo L=cpp M=O2g
	exec scripts/demo.sh $(L) $(M)

cabi:             ## C ABI compatibility test
	exec scripts/cabi_test.sh

repro:            ## build reproducibility test
	$(PY) scripts/repro.py

slides: report    ## build the presentation PDF
	cd slides && pdflatex -interaction=nonstopmode object_file_talk.tex && pdflatex -interaction=nonstopmode object_file_talk.tex

clean:
	rm -rf build

distclean: clean
	rm -f results/*.csv results/*.png results/*.tex results/*.md results/*.txt
