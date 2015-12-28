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
			output, err := execute("deis apps:create %s --buildpack https://example.com", app1Name)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				ContainSubstring("Creating Application... done, created %s", app1Name),
				ContainSubstring("Git remote deis added"),
				ContainSubstring("remote available at ")))
			output, err = execute("deis config:list")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(ContainSubstring("BUILDPACK_URL"))
			output, err = execute("deis apps:destroy --app=%s --confirm=%s", app1Name, app1Name)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				ContainSubstring("Destroying %s...", app1Name),
				ContainSubstring("done in "),
				ContainSubstring("Git remote deis removed")))
		})
	})

	Context("with a deployed app", func() {
		repository := "https://github.com/deis/example-go.git"
		It("can clone the example-go repository", func() {
			output, err := execute("git clone %s", repository)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				ContainSubstring("Cloning into "),
				ContainSubstring("done.")))
			_, err = execute("cd example-go")
			Expect(err).NotTo(HaveOccurred())
			output, err = execute("deis apps:create %s", app2Name)
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				ContainSubstring("Creating Application... done, created %s", app2Name),
				ContainSubstring("Git remote deis added"),
				ContainSubstring("remote available at ")))
			output, err = execute("git push deis master")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				ContainSubstring("-----> Launching..."),
				ContainSubstring("done, %s:v2 deployed to Deis", app2Name)))
		})

		It("can't create an existing app", func() {
			output, err := execute("deis apps:create %s", app1Name)
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("This field must be unique"))
		})

		It("can get app info", func() {
			output, err := execute("deis info")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				HavePrefix("=== %s Application", app2Name),
				ContainSubstring("=== %s Processes", app2Name),
				ContainSubstring(".1 up (v"),
				ContainSubstring("=== %s Domains", app2Name)))
		})

		It("can get app logs", func() {
			output, err := execute("deis logs")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				ContainSubstring("%s[deis-controller]: %s created initial release", app2Name, testUser),
				ContainSubstring("%s[deis-controller]: %s deployed", app2Name, testUser),
				ContainSubstring("%s[deis-controller]: %s scaled containers", app2Name, testUser)))
		})

		// TODO: how to test "deis open" which spawns a browser?
		XIt("can open the app's URL", func() {
			_, err := execute("deis open")
			Expect(err).NotTo(HaveOccurred())
		})

		It("can't open a bogus app URL", func() {
			output, err := execute("deis open -a %s", getRandAppName())
			Expect(err).To(HaveOccurred())
			Expect(output).To(ContainSubstring("404 NOT FOUND"))
		})

		It("can run a command in the app environment", func() {
			output, err := execute("deis apps:run echo Hello, 世界")
			Expect(err).NotTo(HaveOccurred())
			Expect(output).To(SatisfyAll(
				HavePrefix("Running 'echo Hello, 世界'..."),
				HaveSuffix("Hello, 世界\n")))
		})

		// TODO: this requires a second user account
		XIt("can transfer the app to another owner", func() {
		})
	})
})
