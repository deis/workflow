package _tests_test

import (
	"fmt"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Releases", func() {
	appName := getRandAppName()
	Context("with no app", func() {
		It("can create an app", func() {
			output, err := execute("deis apps:create %s --no-remote", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring(fmt.Sprintf("Creating Application... done, created %s", appName)))
		})
		It("can deploy the app", func() {
			output, err := execute("deis pull deis/example-go -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("Creating build... done"))
		})
	})

	Context("with a deployed app", func() {
		It("can list releases", func() {
			output, err := execute("deis releases:list -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				HavePrefix("=== %s Releases", appName),
				MatchRegexp(`v1\t.*\t%s created initial release`, testUser),
				MatchRegexp(`v2\t.*\t%s deployed \w+`, testUser)),
			)
		})

		It("can rollback to a previous release", func() {
			output, err := execute("deis releases:rollback v1 -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				HavePrefix("Rolling back to"),
				ContainSubstring("...done"),
			))
		})

		It("can get info on releases", func() {
			output, err := execute("deis releases:info v1 -a %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				HavePrefix("=== %s Release v1", appName),
				MatchRegexp(`config:\s+[\w-]+`),
				MatchRegexp(`owner:\s+%s`, testUser),
				MatchRegexp(`summary:\s+%s \w+`, testUser),
				// the below updated date has to match a string like 2015-12-22T21:20:31UTC
				MatchRegexp(`updated:\s+[0-9]+-[0-9]+-[A-Z0-9]+:[0-9]+:[A-Z0-9:-]+`, appName),
				MatchRegexp(`uuid:\s+[\w-]+`)))
		})
	})
})
