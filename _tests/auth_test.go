package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/onsi/gomega/gbytes"
	"github.com/onsi/gomega/gexec"
)

var _ = Describe("Auth", func() {
	Context("when logged out", func() {
		BeforeEach(func() {
			logout()
		})

		It("won't print the current user", func() {
			sess, err := start("deis auth:whoami")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(1))
			Eventually(sess.Err).Should(gbytes.Say("Not logged in"))
		})
	})

	Context("when logged in", func() {
		It("can log out", func() {
			logout()
		})

		It("won't register twice", func() {
			cmd := "deis register %s --username=%s --password=%s --email=%s"
			out, err := execute(cmd, url, testUser, testPassword, testEmail)
			Expect(err).To(HaveOccurred())
			Expect(out).To(ContainSubstring("Registration failed"))
		})

		It("prints the current user", func() {
			sess, err := start("deis auth:whoami")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("You are %s", testUser))
		})

		It("regenerates the token for the current user", func() {
			sess, err := start("deis auth:regenerate")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Token Regenerated"))
		})
	})

	Context("when logged in as an admin", func() {
		BeforeEach(func() {
			login(url, testAdminUser, testAdminPassword)
		})

		It("regenerates the token for a specified user", func() {
			output, err := execute("deis auth:regenerate -u %s", testUser)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("Token Regenerated"))
		})

		It("regenerates the token for all users", func() {
			output, err := execute("deis auth:regenerate --all")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("Token Regenerated"))
		})
	})
})
