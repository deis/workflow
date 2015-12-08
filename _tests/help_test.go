package _tests_test

import (
	"fmt"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

const noMatch string = "Found no matching command, try 'deis help'"
const usage string = "Usage: deis <command> [<args>...]"

var _ = Describe("Help", func() {

	for _, flag := range []string{"--help", "-h", "help"} {
		It(fmt.Sprintf("prints help on \"%s\"", flag), func() {
			output, err := execute("deis " + flag)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring(usage))
		})
	}

	It("defaults to a usage message", func() {
		output, err := execute("deis")
		Expect(err).To(HaveOccurred())
		Expect(output).To(ContainSubstring(usage))
	})

	It("rejects a bogus command", func() {
		output, err := execute("deis bogus-command")
		Expect(err).To(HaveOccurred())
		Expect(output).To(SatisfyAll(
			ContainSubstring(noMatch),
			ContainSubstring(usage)))
	})
})
