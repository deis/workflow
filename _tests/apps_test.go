package _tests_test

import (
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/onsi/gomega/gbytes"
	"github.com/onsi/gomega/gexec"
)

var _ = Describe("Apps", func() {
	app1Name := getRandAppName()
	app2Name := getRandAppName()
	Context("with a logged-in user", func() {
		BeforeEach(func() {
			login(url, testUser, testPassword)
		})

		It("can't get app info", func() {
			sess, err := start("deis info -a %s", app1Name)
			Expect(err).ToNot(BeNil())
			Eventually(sess).ShouldNot(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("NOT FOUND"))
		})

		It("can't get app logs", func() {
			sess, err := start("deis logs -a %s", app1Name)
			Expect(err).To(BeNil())
			Eventually(sess).ShouldNot(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("NOT FOUND"))
		})

		// TODO: this currently returns "Error: json: cannot unmarshal object into Go value of type []interface {}"
		XIt("can't run a command in the app environment", func() {
			sess, err := start("deis apps:run echo Hello, 世界")
			Expect(err).To(BeNil())
			Eventually(sess).ShouldNot(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("NOT FOUND"))
		})

		It("can create an app", func() {
			sess, err := start("deis apps:create %s", app1Name)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Creating Application... done, created %s", app1Name))
			Eventually(sess).Should(gbytes.Say("Git remote deis added"))
			Eventually(sess).Should(gbytes.Say("remote available at "))

			sess, err = start("deis apps:destroy --confirm=%s", app1Name)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Destroying %s...", app1Name))
			Eventually(sess).Should(gbytes.Say("done in "))
			Eventually(sess).Should(gbytes.Say("Git remote deis removed"))
		})

		It("can create an app with no git remote", func() {
			sess, err := start("deis apps:create %s --no-remote", app1Name)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Creating Application... done, created %s", app1Name))
			Eventually(sess).Should(gbytes.Say("remove available at "))
			Eventually(sess).ShouldNot(gbytes.Say("git remote deis added"))

			sess, err = start("deis apps:destroy --app=%s --confirm=%s", app1Name, app1Name)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Destroying %s...", app1Name))
			Eventually(sess).Should(gbytes.Say("done in "))
			Eventually(sess).ShouldNot(gbytes.Say("Git remote deis removed"))
		})

		It("can create an app with a custom buildpack", func() {
			sess, err := start("deis apps:create %s --buildpack https://example.com", app1Name)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Creating Application... done, created %s", app1Name))
			Eventually(sess).Should(gbytes.Say("Git remote deis added"))
			Eventually(sess).Should(gbytes.Say("remote available at "))

			sess, err = start("deis config:list")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("BUILDPACK_URL"))

			sess, err = start("deis apps:destroy --app=%s --confirm=%s", app1Name, app1Name)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Destroying %s...", app1Name))
			Eventually(sess).Should(gbytes.Say("done in "))
			Eventually(sess).Should(gbytes.Say("Git remote deis removed"))
		})
	})

	Context("with a deployed app", func() {
		repository := "https://github.com/deis/example-go.git"
		It("can clone the example-go repository", func() {
			sess, err := start("git clone %s", repository)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Cloning into "))
			Eventually(sess).Should(gbytes.Say("done."))

			sess, err = start("cd example-go")
			Expect(err).To(BeNil())
			Expect(sess).To(gexec.Exit(0))

			sess, err = start("deis apps:create %s", app2Name)
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Creating Application... done, created %s", app2Name))
			Eventually(sess).Should(gbytes.Say("Git remote deis added"))
			Eventually(sess).Should(gbytes.Say("remote available at "))

			sess, err = start("git push deis master")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("-----> Launching..."))
			Eventually(sess).Should(gbytes.Say("done, %s:v2 deployed to Deis", app2Name))
		})

		It("can't create an existing app", func() {
			sess, err := start("deis apps:create %s", app1Name)
			Expect(err).ToNot(BeNil())
			Eventually(sess).ShouldNot(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("This field must be unique"))
		})

		It("can get app info", func() {
			sess, err := start("deis info")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("=== %s Application", app2Name))
			Eventually(sess).Should(gbytes.Say("=== %s Processes", app2Name))
			Eventually(sess).Should(gbytes.Say(".1 up (v"))
			Eventually(sess).Should(gbytes.Say("=== %s Domains", app2Name))
		})

		It("can get app logs", func() {
			sess, err := start("deis logs")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("%s[deis-controller]: %s created initial release", app2Name, testUser))
			Eventually(sess).Should(gbytes.Say("%s[deis-controller]: %s deployed", app2Name, testUser))
			Eventually(sess).Should(gbytes.Say("%s[deis-controller]: %s scaled containers", app2Name, testUser))
		})

		// TODO: how to test "deis open" which spawns a browser?
		XIt("can open the app's URL", func() {
			sess, err := start("deis open")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
		})

		It("can't open a bogus app URL", func() {
			sess, err := start("deis open -a %s", getRandAppName())
			Expect(err).ToNot(BeNil())
			Eventually(sess).ShouldNot(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("404 NOT FOUND"))
		})

		It("can run a command in the app environment", func() {
			sess, err := start("deis apps:run echo Hello, 世界")
			Expect(err).To(BeNil())
			Eventually(sess).Should(gexec.Exit(0))
			Eventually(sess).Should(gbytes.Say("Running 'echo Hello, 世界'..."))
			Eventually(sess).Should(gbytes.Say("Hello, 世界\n"))
		})

		// TODO: this requires a second user account
		XIt("can transfer the app to another owner", func() {
		})
	})
})
