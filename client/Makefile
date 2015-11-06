include ../includes.mk

# the filepath to this repository, relative to $GOPATH/src
repo_path = github.com/deis/workflow/client

GO_FILES = $(wildcard *.go)
GO_PACKAGES = cmd controller/api controller/client $(wildcard controller/models/*) parser $(wildcard pkg/*)
GO_PACKAGES_REPO_PATH = $(addprefix $(repo_path)/,$(GO_PACKAGES))

COMPONENT = $(notdir $(repo_path))
IMAGE =  $(IMAGE_PREFIX)/$(COMPONENT):$(BUILD_TAG)

bootstrap:
	glide -y glide.yaml up

build:
	CGO_ENABLED=0 go build -a -installsuffix cgo -ldflags '-s' -o deis .
	@$(call check-static-binary,deis)

install: build
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
	@if [ $(shell gofmt -e -l -s $(GO_FILES) $(GO_PACKAGES)) ]; then \
		echo "gofmt check failed:"; gofmt -e -l -s $(GO_FILES) $(GO_PACKAGES); exit 1; \
	fi
	@$(GOVET) $(repo_path) $(GO_PACKAGES_REPO_PATH)
	@for i in $(addsuffix /...,$(GO_PACKAGES)); do \
		$(GOLINT) $$i; \
	done

test-unit:
	$(GOTEST) $(shell glide novendor)
