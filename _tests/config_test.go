package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Config", func() {
	Context("with a deployed app", func() {
		appName := getRandAppName()

		It("can list environment variables", func() {
			output, err := execute("deis apps:create %s", appName)
			Expect(err).NotTo(HaveOccurred(), output)

			output, err = execute("deis config:set FOO=bar -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				ContainSubstring("Creating config"),
				ContainSubstring("FOO      bar"),
				ContainSubstring("=== %s Config", appName),
			))
			output, err = execute("deis config:list -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				ContainSubstring("=== %s Config", appName),
				ContainSubstring("FOO      bar"),
			))
			// TODO: the following won't work as-is because there is no app running
			// "deis run env -a %s"

		})

		It("can set an integer environment variable", func() {
			output, err := execute("deis config:set FOO=1 -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("FOO      1"))
		})

		It("can set an environment variable containing spaces", func() {
			output, err := execute(`deis config:set POWERED_BY=the\ Deis\ team -a %s`, appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("POWERED_BY      the Deis team"))
		})

		It("can set a multi-line environment variable", func() {
			mlString := "This is a\n multiline\r string"
			output, err := execute(`deis config:set FOO="%s" -a %s`, mlString, appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(MatchRegexp(`FOO\s+%s`, mlString))
		})

		It("can set an environment variable with multibyte chars", func() {
			output, err := execute("deis config:set FOO=讲台 -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("FOO             讲台"))
		})

		It("can unset an environment variable", func() {
			output, err := execute("deis config:set FOO=bar -a %s", appName)
			Expect(err).NotTo(HaveOccurred(), output)
			Expect(output).To(ContainSubstring("FOO             bar"))
			output, err = execute("deis config:unset FOO -a %s", appName)
			Expect(err).NotTo(HaveOccurred(), output)
			Expect(output).NotTo(ContainSubstring("FOO"))
		})

		XIt("can pull the configuration to an .env file", func() {

		})

		XIt("can push the configuration from an .env file", func() {

		})
	})
})
