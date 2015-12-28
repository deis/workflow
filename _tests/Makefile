
test-setup:
	go get github.com/onsi/ginkgo/ginkgo
	go get github.com/onsi/gomega

test-integration:
	go test -v -ginkgo.v ./...

build:
# Precompile the test suite into a binary "_tests.test"
	ginkgo build -race -r
