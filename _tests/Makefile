# These environment variables tell the tests where the deis router is, which it uses to communicate with the controller.
# Router's default is to server on 'example.com', so 'deis.example.com' should route to controller.
DEIS_WORKFLOW_SERVICE_HOST ?= deis.example.com
DEIS_WORKFLOW_SERVICE_PORT ?= 80

test-setup:
	go get github.com/onsi/ginkgo/ginkgo
	go get github.com/onsi/gomega

test-integration:
	go test -v ./...

build:
# Precompile the test suite into a binary "_tests.test"
	ginkgo build -race -r
