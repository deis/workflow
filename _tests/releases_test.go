package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/onsi/gomega/gbytes"
	"github.com/onsi/gomega/gexec"
	"time"
)

var _ = Describe("Releases", func() {
	Context("with a deployed app", func() {
		var appName string

		BeforeEach(func() {
			appName = getRandAppName()
			createApp(appName)
		})

		// 500's everytime
		XIt("can deploy the app", func() {
			sess, err := start("deis pull deis/example-go -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess, (10 * time.Minute)).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Creating build... done"))
		})

		It("can list releases", func() {
			sess, err := start("deis releases:list -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess, (1 * time.Minute)).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("=== %s Releases", appName))
			Eventually(sess).Should(gbytes.Say(`v1\s+.*\s+%s created initial release`, testUser))
		})

		It("can rollback to a previous release", func() {
			sess, err := start("deis releases:rollback v1 -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess, (1 * time.Minute)).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say(`Rolling back to`))
			Eventually(sess).Should(gbytes.Say(`...done`))
		})

		It("can get info on releases", func() {
			sess, err := start("deis releases:info v1 -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess, (1 * time.Minute)).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("=== %s Release v1", appName))
			Eventually(sess).Should(gbytes.Say(`config:\s+[\w-]+`))
			Eventually(sess).Should(gbytes.Say(`owner:\s+%s`, testUser))
			Eventually(sess).Should(gbytes.Say(`summary:\s+%s \w+`, testUser))
			// the below updated date has to match a string like 2015-12-22T21:20:31UTC
			Eventually(sess).Should(gbytes.Say(`updated:\s+[\w\-\:]+UTC`))
			Eventually(sess).Should(gbytes.Say(`uuid:\s+[0-9a-f\-]+`))
		})
	})
})
