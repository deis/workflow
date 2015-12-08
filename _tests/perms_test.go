package _tests_test

import (
	. "github.com/onsi/ginkgo"
	// . "github.com/onsi/gomega"
)

var _ = Describe("Perms", func() {
	Context("when logged in as an admin user", func() {

		XIt("can create, list, and delete admin permissions", func() {
			// "deis perms:create %s --admin", user
			// "deis perms:list --app=%s", app
			// "deis perms:delete %s --admin", user
			// "deis perms:list --app=%s", app
		})

		XIt("can create, list, and delete app permissions", func() {
			// "deis perms:create %s --app=%s", user, app
			// "deis perms:list --app=%s", app
			// "deis perms:delete %s --app=%s", user, app
			// "deis perms:list --app=%s", app
		})
	})

	Context("when logged in as a normal user", func() {

		XIt("can't create, list, or delete admin permissions", func() {
			// "deis perms:create %s --admin", user
			// "deis perms:list --app=%s", app
			// "deis perms:delete %s --admin", user
			// "deis perms:list --app=%s", app
		})

		XIt("can create, list, and delete app permissions", func() {
			// "deis perms:create %s --app=%s", user, app
			// "deis perms:list --app=%s", app
			// "deis perms:delete %s --app=%s", user, app
			// "deis perms:list --app=%s", app
		})
	})
})
