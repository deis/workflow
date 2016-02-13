export GO15VENDOREXPERIMENT=1

# the filepath to this repository, relative to $GOPATH/src
repo_path = github.com/deis/workflow/client

DEV_ENV_IMAGE := quay.io/deis/go-dev:0.5.0
DEV_ENV_WORK_DIR := /go/src/${repo_path}
DEV_ENV_PREFIX := docker run --rm -e GO15VENDOREXPERIMENT=1 -e CGO_ENABLED=0 -v ${CURDIR}:${DEV_ENV_WORK_DIR} -w ${DEV_ENV_WORK_DIR}
DEV_ENV_CMD := ${DEV_ENV_PREFIX} ${DEV_ENV_IMAGE}
DIST_DIR := _dist

GO_FILES = $(wildcard *.go)
GO_PACKAGES = cmd controller/api controller/client $(wildcard controller/models/*) parser $(wildcard pkg/*)
GO_PACKAGES_REPO_PATH = $(addprefix $(repo_path)/,$(GO_PACKAGES))
GOFMT = gofmt -e -l -s
GOTEST = go test --cover --race -v

VERSION := $(shell git describe --tags --abbrev=0 2>/dev/null)+$(shell git rev-parse --short HEAD)

define check-static-binary
  if file $(1) | egrep -q "(statically linked|Mach-O)"; then \
    echo -n ""; \
  else \
    echo "The binary file $(1) is not statically linked. Build canceled"; \
    exit 1; \
  fi
endef

bootstrap:
	${DEV_ENV_CMD} glide install

glideup:
	${DEV_ENV_CMD} glide up

build:
	${DEV_ENV_CMD} make binary-build
	@$(call check-static-binary,deis)

build-all:
	gox -verbose \
	-os="linux darwin " \
	-arch="amd64 386" \
	-output="$(DIST_DIR)/deis-${VERSION}-{{.OS}}-{{.Arch}}" .

binary-build:
	go build -a -installsuffix cgo -ldflags '-s' -o deis .

dist: build-all

install:
	cp deis $$GOPATH/bin

installer: build
	@if [ ! -d makeself ]; then git clone -b single-binary https://github.com/deis/makeself.git; fi
	PATH=./makeself:$$PATH BINARY=deis makeself.sh --bzip2 --current --nox11 . \
		deis-cli-`cat deis-version`-`go env GOOS`-`go env GOARCH`.run \
		"Deis CLI" "echo \
		&& echo 'deis is in the current directory. Please' \
		&& echo 'move deis to a directory in your search PATH.' \
		&& echo \
		&& echo 'See http://docs.deis.io/ for documentation.' \
		&& echo"

setup-gotools:
	go get -u github.com/golang/lint/golint
	go get -u golang.org/x/tools/cmd/cover
	go get -u golang.org/x/tools/cmd/vet

test: test-style test-unit

test-style:
	@if [ $(shell $(GOFMT) $(GO_FILES) $(GO_PACKAGES)) ]; then \
		echo "gofmt check failed:"; $(GOFMT) $(GO_FILES) $(GO_PACKAGES); exit 1; \
	fi
	@go vet $(repo_path) $(GO_PACKAGES_REPO_PATH)
	@for i in $(addsuffix /...,$(GO_PACKAGES)); do \
		golint $$i; \
	done

test-unit:
	$(GOTEST) $(shell glide novendor)
