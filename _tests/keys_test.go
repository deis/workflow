package _tests_test

import (
	"os"
	"os/user"
	"path"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Keys", func() {
	key := testUser

	Context("when logged in as a normal user", func() {
		BeforeEach(func() {
			login(url, testUser, testPassword)
			createKey(testUser)
		})

		AfterEach(func() {
			// remove the generated ssh key
			var home string
			if user, err := user.Current(); err != nil {
				home = "~"
			} else {
				home = user.HomeDir
			}
			path := path.Join(home, ".ssh", testUser)
			err := os.Remove(path)
			Expect(err).NotTo(HaveOccurred())
			err = os.Remove(path + ".pub")
			Expect(err).NotTo(HaveOccurred())
		})

		It("can add, list, and remove a key", func() {
			output, err := execute("deis keys:add ~/.ssh/%s.pub", key)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("Uploading %s.pub to deis... done", key))
			output, err = execute("deis keys:list")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("%s ssh-rsa", key))
			output, err = execute("deis keys:remove %s", key)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("Removing %s SSH Key... done", key))
			output, err = execute("deis keys")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).NotTo(ContainSubstring("%s ssh-rsa", key))
		})
	})
})
