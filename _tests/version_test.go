package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Version", func() {

	It("prints its version", func() {
		output, err := execute("deis --version")
		Expect(err).NotTo(HaveOccurred())
		// TODO: read the expected version from ../client/deis-version?
		Expect(output).To(Equal("2.0.0-dev\n"))
	})
})
