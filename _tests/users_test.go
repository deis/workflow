package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Users", func() {
	Context("when logged in as an admin user", func() {
		BeforeEach(func() {
			login(url, testAdminUser, testAdminPassword)
		})

		It("can list all users", func() {
			output, err := execute("deis users:list")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				HavePrefix("=== Users"),
				ContainSubstring(testUser),
				ContainSubstring(testAdminUser)))
		})
	})

	Context("when logged in as a normal user", func() {
		BeforeEach(func() {
			login(url, testUser, testPassword)
		})

		It("can't list all users", func() {
			output, err := execute("deis users:list")
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("403 FORBIDDEN"))
		})
	})
})
