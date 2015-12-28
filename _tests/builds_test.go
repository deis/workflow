package _tests_test

import (
	"fmt"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Builds", func() {
	appName := getRandAppName()
	Context("with a logged-in user", func() {
		BeforeEach(func() {
			login(url, testUser, testPassword)
		})

		Context("with no app", func() {
			It("can create an app", func() {
				output, err := execute("deis apps:create %s --no-remote", appName)
				Expect(err).NotTo(HaveOccurred())
				Expect(output).To(ContainSubstring(fmt.Sprintf("Creating Application... done, created %s", appName)))
			})
			It("can deploy the app", func() {
				output, err := execute("deis builds:create %s -a %s", "deis/example-go", appName)
				Expect(err).NotTo(HaveOccurred())
				Expect(output).To(ContainSubstring("Creating build... done"))
			})
			It("can list app builds", func() {
				output, err := execute("deis builds:list --app=%s", appName)
				Expect(err).NotTo(HaveOccurred())
				Expect(output).To(SatisfyAll(
					MatchRegexp(`[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}`)))
			})
		})

		Context("with a deployed app", func() {

			XIt("can list app builds", func() {
			})

			XIt("can create a build from an existing image (\"deis pull\")", func() {

			})
		})

	})
})
