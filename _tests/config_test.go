package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Config", func() {
	Context("with a deployed app", func() {
		appName := getRandAppName()
		BeforeEach(func() {
			login(url, testUser, testPassword)
		})

		It("can create a new app", func() {
			output, err := execute("deis apps:create %s", appName)
			Expect(err).To(BeNil())
			Expect(output).To(SatisfyAll(
				ContainSubstring("Creating Application... done, created %s", appName),
				ContainSubstring("Git remote deis added"),
				ContainSubstring("remote available at ")))
		})

		It("can list environment variables", func() {
			out, err := execute("deis config:set FOO=bar -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(out).To(SatisfyAll(
				ContainSubstring("Creating config... done"),
				ContainSubstring("FOO      bar"),
				ContainSubstring("=== %s Config", appName),
			))
			out, err = execute("deis config:list -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(out).To(SatisfyAll(
				ContainSubstring("=== %s Config", appName),
				ContainSubstring("FOO      bar"),
			))
			// TODO: the following won't work as-is because there is no app running
			// "deis run env -a %s"

		})

		It("can set an integer environment variable", func() {
			out, err := execute("deis config:set FOO=1 -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(out).To(ContainSubstring("FOO      1"))
		})

		It("can set an environment variable containing spaces", func() {
			out, err := execute(`deis config:set POWERED_BY=the\ Deis\ team -a %s`, appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(out).To(ContainSubstring("POWERED_BY      the Deis team"))
		})

		It("can set a multi-line environment variable", func() {
			out, err := execute(`deis config:set FOO=This\ is\ a\
				multiline\ string -a %s`, appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(out).To(ContainSubstring(`FOO             This\ is\ a\
multiline\ string`))
		})

		It("can set an environment variable with multibyte chars", func() {
			out, err := execute("deis config:set FOO=讲台 -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(out).To(ContainSubstring("FOO             讲台"))
		})

		It("can unset an environment variable", func() {
			out, err := execute("deis config:set FOO=bar -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(out).To(ContainSubstring("FOO             bar"))
			out, err = execute("deis config:unset FOO -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(out).NotTo(ContainSubstring("FOO"))
		})

		XIt("can pull the configuration to an .env file", func() {

		})

		XIt("can push the configuration from an .env file", func() {

		})
	})
})
