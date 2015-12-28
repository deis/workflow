package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/onsi/gomega/gbytes"
	"github.com/onsi/gomega/gexec"
)

var _ = Describe("Releases", func() {
	appName := getRandAppName()
	Context("with no app", func() {
		It("can create an app", func() {
			sess, err := start("deis apps: create %s --no-remote", appName)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Creating Application... done, created %s", appName))
		})
		It("can deploy the app", func() {
			sess, err := start("deis pull deis/example-go -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Creating build... done"))
		})
	})

	Context("with a deployed app", func() {
		It("can list releases", func() {
			sess, err := start("deis releases:list -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("=== %s Releases", appName))
			Eventually(sess).Should(gbytes.Say(`v1\t.*\t%s created initial release`, testUser))
			Eventually(sess).Should(gbytes.Say(`v2\t.*\t%s deployed \w+`, testUser))
		})

		It("can rollback to a previous release", func() {
			sess, err := start("deis releases:rollback v1 -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Rolling back to"))
			Eventually(sess).Should(gbytes.Say("...done"))
		})

		It("can get info on releases", func() {
			sess, err := start("deis releases:info v1 -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("=== %s Release v1", appName))
			Eventually(sess).Should(gbytes.Say(`config:\s+[\w-]+`))
			Eventually(sess).Should(gbytes.Say(`owner:\s+%s`, testUser))
			Eventually(sess).Should(gbytes.Say(`summary:\s+%s \w+`, testUser))
			// the below updated date has to match a string like 2015-12-22T21:20:31UTC
			Eventually(sess).Should(gbytes.Say(`updated:\s+[0-9]+-[0-9]+-[A-Z0-9]+:[0-9]+:[A-Z0-9:-]+`, appName))
			Eventually(sess).Should(gbytes.Say(`uuid:\s+[\w-]+`))
		})
	})
})
