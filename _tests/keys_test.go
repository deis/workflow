package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Keys", func() {
	It("can list and remove a key", func() {
		output, err := execute("deis keys:list")
		Expect(err).NotTo(HaveOccurred())
		Expect(output).To(ContainSubstring("%s ssh-rsa", keyName))
		output, err = execute("deis keys:remove %s", keyName)
		Expect(err).NotTo(HaveOccurred())
		Expect(output).To(ContainSubstring("Removing %s SSH Key... done", keyName))
		output, err = execute("deis keys")
		Expect(err).NotTo(HaveOccurred())
		Expect(output).NotTo(ContainSubstring("%s ssh-rsa", keyName))
	})
})
