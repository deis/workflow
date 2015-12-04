# Makefile for MkDocs documentation
#

# You can set these variables from the command line.
BUILDDIR        = _build
MKDOCS          = mkdocs
MKDOCSBUILDOPTS = --clean --strict --verbose
MKDOCSBUILD     = $(MKDOCS) build $(MKDOCSBUILDOPTS)

build:
	$(MKDOCSBUILD) --site-dir $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

clean:
	rm -rf $(BUILDDIR)/*

deps:
	pip install -r requirements.txt

test: build
	grep -q '<h1 id="welcome">Welcome</h1>' _build/html/index.html
	@echo
	@echo "Test finished. The HTML pages are in $(BUILDDIR)/html."
