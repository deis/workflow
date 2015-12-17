package _tests_test

import (
	. "github.com/onsi/ginkgo"
	// . "github.com/onsi/gomega"
)

var _ = Describe("Domains", func() {
	Context("with a deployed app", func() {

		XIt("can add, list, and remove domains", func() {
			// "deis domains:list --app=%s", app
			// "deis domains:add %s --app=%s", domain, app
			// "deis domains:list --app=%s", app
			// curl app at both root and custom domain
			// "deis domains:remove %s --app=%s", domain, app
			// "deis domains:list --app=%s", app
			// curl app at both root and custom domain, custom should fail
		})

		XIt("can add, list, and remove certs", func() {
			// "deis domains:add %s --app=%s", domain, app
			// "deis certs:list", app
			// "deis certs:add %s %s", certPath, keyPath
			// wait for 60 seconds until cert generation is done?
			// curl the custom SSL endpoint
			// "deis certs:remove %s", domain
			// "deis certs:list", app
			// curl the custom SSL endpoint, should fail
			// curl app at both root and custom domain, custom should fail
			// "deis domains:remove %s --app=%s", domain, app
		})
	})
})
