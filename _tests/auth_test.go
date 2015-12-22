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
			Expect(execute("deis auth:whoami")).To(BeASuccessfulCommandWithOutputMatching(
				ContainSubstring("Not logged in."),
				ContainSubstring(testUser),
			))
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
			out := execute(cmd, url, testUser, testPassword, testEmail)
			Expect(out.err).To(HaveOccurred())
			Expect(out.str).To(ContainSubstring("Registration failed"))
		})

		It("prints the current user", func() {
			Expect(execute("deis auth:whoami")).To(SucceedWithOutput(
				ContainSubstring("You are %s", testUser),
			))
		})

		It("regenerates the token for the current user", func() {
			Expect(execute("deis auth:regenerate")).To(SucceedWithOutput(
				ContainSubstring("Token Regenerated"),
			))
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
