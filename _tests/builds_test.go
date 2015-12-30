package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/onsi/gomega/gbytes"
	"github.com/onsi/gomega/gexec"
	"time"
)

var _ = Describe("Builds", func() {
	Context("with a logged-in user", func() {
		Context("with no app", func() {
			var appName string

			BeforeEach(func() {
				appName = getRandAppName()
				// This returns 404 NOT FOUND
				cmd, err := start("deis builds:create %s -a %s", "deis/example-go:latest", appName)
				Expect(err).NotTo(HaveOccurred())
				Eventually(cmd, (1 * time.Minute)).Should(gexec.Exit(0))
				Eventually(cmd).Should(gbytes.Say("Creating build... done"))
			})

			XIt("can list app builds", func() {
				cmd, err := start("deis builds:list --app=%s", appName)
				Expect(err).NotTo(HaveOccurred())
				Eventually(cmd, (1 * time.Minute)).Should(gexec.Exit(0))
				Eventually(cmd).Should(gbytes.Say(`[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}`))
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
