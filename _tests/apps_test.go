package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/onsi/gomega/gbytes"
	"github.com/onsi/gomega/gexec"
	"time"
)

var _ = Describe("Apps", func() {
	var appName string

	BeforeEach(func() {
		appName = getRandAppName()
	})

	Context("with no app", func() {

		It("can't get app info", func() {
			sess, _ := start("deis info -a %s", appName)
			Eventually(sess).Should(gexec.Exit(1))
			Eventually(sess.Err).Should(gbytes.Say("NOT FOUND"))
		})

		It("can't get app logs", func() {
			sess, err := start("deis logs -a %s", appName)
			Expect(err).To(BeNil())
			Eventually(sess).ShouldNot(gexec.Exit(0))
			Eventually(sess.Err).Should(gbytes.Say("NOT FOUND"))
		})

		// TODO: this currently returns "Error: json: cannot unmarshal object into Go value of type []interface {}"
		XIt("can't run a command in the app environment", func() {
			sess, err := start("deis apps:run echo Hello, 世界")
			Expect(err).To(BeNil())
			Eventually(sess).ShouldNot(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("NOT FOUND"))
		})

	})

	Context("when creating an app", func() {
		var cleanup bool

		BeforeEach(func() {
			cleanup = true
			appName = getRandAppName()
		})

		AfterEach(func() {
			if cleanup {
				destroyApp(appName)
			}
		})

		It("creates an app with a git remote", func() {
			cmd, err := start("deis apps:create %s", appName)
			Expect(err).NotTo(HaveOccurred())
			Eventually(cmd).Should(gbytes.Say("created %s", appName))
			Eventually(cmd).Should(gbytes.Say(`Git remote deis added`))
			Eventually(cmd).Should(gbytes.Say(`remote available at `))
		})

		It("creates an app with no git remote", func() {
			cmd, err := start("deis apps:create %s --no-remote", appName)
			Expect(err).NotTo(HaveOccurred())
			Eventually(cmd).Should(SatisfyAll(
				gbytes.Say("created %s", appName),
				gbytes.Say("remote available at ")))
			Eventually(cmd).ShouldNot(gbytes.Say("Git remote deis added"))

			cleanup = false
			cmd = destroyApp(appName)
			Eventually(cmd).ShouldNot(gbytes.Say("Git remote deis removed"))
		})

		It("creates an app with a custom buildpack", func() {
			sess, err := start("deis apps:create %s --buildpack https://example.com", appName)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("created %s", appName))
			Eventually(sess).Should(gbytes.Say("Git remote deis added"))
			Eventually(sess).Should(gbytes.Say("remote available at "))

			sess, err = start("deis config:list")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("BUILDPACK_URL"))
		})
	})

	Context("with a deployed app", func() {
		var appName string

		BeforeEach(func() {
			appName = getRandAppName()
			cmd := createApp(appName)
			Eventually(cmd).Should(SatisfyAll(
				gbytes.Say("Git remote deis added"),
				gbytes.Say("remote available at ")))

			cmd, err := start("GIT_SSH=%s git push deis master", gitSSH)
			Expect(err).NotTo(HaveOccurred())
			Eventually(cmd.Err, "2m").Should(gbytes.Say("done, %s:v2 deployed to Deis", appName))
		})

		AfterEach(func() {
			destroyApp(appName)
		})

		It("can't create an existing app", func() {
			output, err := execute("deis apps:create %s", appName)
			Expect(err).To(HaveOccurred(), output)

			Expect(output).To(ContainSubstring("This field must be unique"))
		})

		It("can get app info", func() {
			sess, err := start("deis info")
			Expect(err).NotTo(HaveOccurred())

			Eventually(sess).Should(gbytes.Say("=== %s Processes", appName))
			Eventually(sess).Should(SatisfyAny(
				gbytes.Say("web.1 initialized"),
				gbytes.Say("web.1 up")))
			Eventually(sess).Should(gbytes.Say("=== %s Domains", appName))
		})

		// V broken
		XIt("can get app logs", func() {
			cmd, err := start("deis logs")
			Expect(err).NotTo(HaveOccurred())
			Eventually(cmd).Should(SatisfyAll(
				gbytes.Say("%s\\[deis-controller\\]\\: %s created initial release", appName, testUser),
				gbytes.Say("%s\\[deis-controller\\]\\: %s deployed", appName, testUser),
				gbytes.Say("%s\\[deis-controller\\]\\: %s scaled containers", appName, testUser)))
		})

		// TODO: how to test "deis open" which spawns a browser?
		XIt("can open the app's URL", func() {
			sess, err := start("deis open")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
		})

		// TODO: be more useful
		XIt("can't open a bogus app URL", func() {
			cmd, err := start("deis open -a %s", getRandAppName())
			Expect(err).To(HaveOccurred())
			Eventually(cmd).Should(gbytes.Say("404 NOT FOUND"))
		})

		// V broken
		XIt("can run a command in the app environment", func() {
			cmd, err := start("deis apps:run echo Hello, 世界")
			Expect(err).NotTo(HaveOccurred())
			Eventually(cmd, (1 * time.Minute)).Should(SatisfyAll(
				HavePrefix("Running 'echo Hello, 世界'..."),
				HaveSuffix("Hello, 世界\n")))
		})

		// TODO: this requires a second user account
		XIt("can transfer the app to another owner", func() {
		})
	})
})
