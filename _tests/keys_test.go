package _tests_test

import (
	"os"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Keys", func() {
	key := testUser

	BeforeEach(func() {
		addKey(key)
	})

	AfterEach(func() {
		// remove the generated ssh key
		key := testUser
		execute("deis keys:remove %s", key)
		err := os.Remove(key)
		Expect(err).NotTo(HaveOccurred())
		err = os.Remove(key + ".pub")
		Expect(err).NotTo(HaveOccurred())
	})

	Context("with a new key", func() {

		It("can add the key", func() {
			output, err := execute("deis keys:add %s.pub", key)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("Uploading %s.pub to deis... done", key))
			output, err = execute("deis keys:list")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("%s@deis.com", key))
		})

		It("can remove the key", func() {
			output, err := execute("deis keys:remove %s@deis.com", key)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("Removing %s@deis.com SSH Key... done", key))
			output, err = execute("deis keys")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).NotTo(ContainSubstring("%s@deis.com", key))
		})
	})
})
