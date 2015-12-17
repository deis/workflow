package _tests_test

import (
	. "github.com/onsi/ginkgo"
	// . "github.com/onsi/gomega"
)

var _ = Describe("deis", func() {
	Context("with a deployed app", func() {

		XIt("can scale upward", func() {
			// "deis ps:scale web=5 --app=%s"
			// "deis ps:list --app=%s"
			// curl app
			// "deis ps:scale web=1 --app=%s"
			// "deis ps:list --app=%s"
			// curl app
		})

		XIt("can scale down to 0", func() {
			// "deis ps:scale web=0 --app=%s"
			// "deis ps:list --app=%s"
			// curl app
			// "deis ps:scale web=1--app=%s"
			// "deis ps:list --app=%s"
			// curl app
		})

		XIt("can restart all processes", func() {
			// "deis ps:scale web=5 --app=%s"
			// "deis ps:list --app=%s"
			// curl app
			// "deis ps:restart web --app=%s"
			// "deis ps:list --app=%s"
			// curl app
		})

		XIt("can restart a specific process", func() {
			// "deis ps:restart web.1 --app=%s"
			// "deis ps:list --app=%s"
			// curl app
		})
	})
})
