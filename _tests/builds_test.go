package _tests_test

import (
	. "github.com/onsi/ginkgo"
	// . "github.com/onsi/gomega"
)

var _ = Describe("Builds", func() {
	Context("with a deployed app", func() {

		It("can list app builds", func() {
			// "deis builds:list --app=%s", app
		})

		It("can create a build from an existing image (\"deis pull\")", func() {
			// "deis builds:create %s --app=%s", image, app
			// curl app
			// `deis pull %s -a %s --procfile="worker: while true; do echo hi; sleep 3; done"`, image, app
			// "deis ps:scale worker=1"
			// "deis logs --app=%s", app
		})
	})
})
