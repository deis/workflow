package _tests_test

import (
	. "github.com/onsi/ginkgo"
	// . "github.com/onsi/gomega"
)

var _ = Describe("Config", func() {
	Context("with a deployed app", func() {

		XIt("can list environment variables", func() {
			// "deis config:set FOO=bar--app=%s"
			// "deis run env --app=%s"
			// "deis config:list --app=%s"
		})

		XIt("can set an integer environment variable", func() {
			// "deis config:set FOO=10 --app=%s"
			// "deis run env --app=%s"
		})

		XIt("can set an environment variable containing spaces", func() {
			// "config:set POWERED_BY=\"the Deis team\" --app={{.AppName}}"
			// "deis run env --app=%s"
		})

		XIt("can set a multi-line environment variable", func() {
			// `deis config:set FOO="This is a
			//multiline string" --app={{.AppName}}`
			// "deis run env --app=%s"
		})

		XIt("can set an environment variable with multibyte chars", func() {
			// "deis config:set FOO=讲台 --app=%s"
			// "deis run env --app=%s"
		})

		XIt("can unset an environment variable", func() {
			// "deis config:set FOO=bar --app=%s"
			// "deis run env --app=%s"
			// "deis config:unset FOO --app=%s"
			// "deis run env --app=%s"
		})

		XIt("can pull the configuration to an .env file", func() {

		})

		XIt("can push the configuration from an .env file", func() {

		})
	})
})
