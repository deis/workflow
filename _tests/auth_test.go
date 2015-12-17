package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Auth", func() {
	Context("when logged out", func() {
		BeforeEach(func() {
			logout()
		})

		It("won't print the current user", func() {
			output, err := execute("deis auth:whoami")
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("Not logged in."))
			Expect(output).NotTo(ContainSubstring(testUser))
		})
	})

	Context("when logged in", func() {
		BeforeEach(func() {
			login(url, testUser, testPassword)
		})

		It("can log out", func() {
			logout()
		})

		It("won't register twice", func() {
			cmd := "deis register %s --username=%s --password=%s --email=%s"
			output, err := execute(cmd, url, testUser, testPassword, testEmail)
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("Registration failed"))
		})

		It("prints the current user", func() {
			output, err := execute("deis auth:whoami")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("You are %s", testUser))
		})

		It("regenerates the token for the current user", func() {
			output, err := execute("deis auth:regenerate")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("Token Regenerated"))
		})
	})

	Context("when logged in as an admin", func() {
		BeforeEach(func() {
			login(url, testAdminUser, testAdminPassword)
		})

		It("regenerates the token for a specified user", func() {
			output, err := execute("deis auth:regenerate -u %s", testUser)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("???"))
		})

		It("regenerates the token for all users", func() {
			output, err := execute("deis auth:regenerate --all")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("???"))
		})
	})
})
