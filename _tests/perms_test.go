package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Perms", func() {
	Context("when logged in as an admin user", func() {
		BeforeEach(func() {
			login(url, testAdminUser, testAdminPassword)
		})

		It("can create, list, and delete admin permissions", func() {
			output, err := execute("deis perms:create %s --admin", testUser)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(
				ContainSubstring("Adding %s to system administrators... done\n", testUser))
			output, err = execute("deis perms:list --admin")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				HavePrefix("=== Administrators"),
				ContainSubstring(testUser),
				ContainSubstring(testAdminUser)))
			output, err = execute("deis perms:delete %s --admin", testUser)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(
				ContainSubstring("Removing %s from system administrators... done", testUser))
			output, err = execute("deis perms:list --admin")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				HavePrefix("=== Administrators"),
				ContainSubstring(testAdminUser)))
			Expect(output).NotTo(ContainSubstring(testUser))
		})

		// TODO: need an app already deployed--do this in BeforeSuite
		XIt("can create, list, and delete app permissions", func() {
			// "deis perms:create %s --app=%s", user, app
			// "deis perms:list --app=%s", app
			// "deis perms:delete %s --app=%s", user, app
			// "deis perms:list --app=%s", app
		})
	})

	Context("when logged in as a normal user", func() {
		It("can't create, list, or delete admin permissions", func() {
			output, err := execute("deis perms:create %s --admin", testAdminUser)
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("403 FORBIDDEN"))
			output, err = execute("deis perms:list --admin")
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("403 FORBIDDEN"))
			output, err = execute("deis perms:delete %s --admin", testAdminUser)
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("403 FORBIDDEN"))
			output, err = execute("deis perms:list --admin")
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("403 FORBIDDEN"))
		})

		// TODO: need an app already deployed--do this in BeforeSuite
		XIt("can create, list, and delete app permissions", func() {
			// "deis perms:create %s --app=%s", user, app
			// "deis perms:list --app=%s", app
			// "deis perms:delete %s --app=%s", user, app
			// "deis perms:list --app=%s", app
		})
	})
})
