package _tests_test

import (
	. "github.com/onsi/ginkgo"
	// . "github.com/onsi/gomega"
)

var _ = Describe("Releases", func() {
	Context("with a deployed app", func() {

		// XIt("can list releases", func() {
		// 	output, err := execute("deis releases:list --app=%s", appName)
		// 	Expect(err).NotTo(HaveOccurred())
		// 	Expect(output).To(SatisfyAll(
		// 		HavePrefix("=== %s Releases", appName),
		// 		MatchRegexp(`v1\t.*\t%s created initial release`, username),
		// 		MatchRegexp(`v2\t.*\t%s deployed \w+`, username)))
		// })
		//
		// XIt("can rollback to a previous release", func() {
		// 	output, err := execute("deis releases:rollback v2 --app=%s", appName)
		// 	Expect(err).NotTo(HaveOccurred())
		//
		// 	Expect
		// 	regexp := `asdf`
		// 	Expect(output)
		// })
		//
		// XIt("can get info on releases", func() {
		// 	output, err := execute("deis releases:info %s --app=%s", version, appName)
		// 	Expect(err).NotTo(HaveOccurred())
		// 	Expect(output).To(SatisfyAll(
		// 		HavePrefix("=== %s Release v2", appName),
		// 		MatchRegexp(`build:\s+[\w-]+`),
		// 		MatchRegexp(`config:\s+[\w-]+`),
		// 		MatchRegexp(`owner:\s+%s`, username),
		// 		MatchRegexp(`summary:\s+%s deployed \w+`, username),
		// 		MatchRegexp(`uuid:\s+[\w-]+`)))
		// })
	})
})
