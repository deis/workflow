# Makefile for MkDocs documentation
#

# You can set these variables from the command line.
BUILDDIR        ?= _build/html
MKDOCS          = mkdocs
MKDOCSBUILDOPTS = --clean --strict --verbose
MKDOCSBUILD     = $(MKDOCS) build $(MKDOCSBUILDOPTS)
MKDOCSSERVE     = $(MKDOCS) serve -a 0.0.0.0:8000

SHORT_NAME ?= workflow
VERSION ?= git-$(shell git rev-parse --short HEAD)
IMAGE := ${SHORT_NAME}:${VERSION}

REPO_PATH := github.com/deis/${SHORT_NAME}
DEV_ENV_WORK_DIR := /src/${REPO_PATH}
DEV_ENV_PREFIX := docker run --rm -v ${CURDIR}:${DEV_ENV_WORK_DIR} -w ${DEV_ENV_WORK_DIR} -p 8000:8000
DEV_ENV_CMD := ${DEV_ENV_PREFIX} ${DEV_ENV_IMAGE}

build:
	$(MKDOCSBUILD) --site-dir $(BUILDDIR)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)."

serve:
	$(MKDOCSSERVE)

clean:
	rm -rf $(BUILDDIR)/*

deps:
	pip install -r requirements.txt

test: build
	grep -q '<title>Deis Documentation</title>' _build/html/index.html
	@echo
	@echo "Test finished. The HTML pages are in $(BUILDDIR)."

docker-build:
	docker build --rm -t ${IMAGE} .

docker-serve:
	${DEV_ENV_CMD} ${IMAGE}
