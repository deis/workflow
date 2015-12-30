package _tests_test

import (
	"fmt"
	"io/ioutil"
	"math/rand"
	"os"
	"os/exec"
	"path"
	"strings"
	"testing"
	"time"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/onsi/gomega/gbytes"
	"github.com/onsi/gomega/gexec"
)

const (
	deisWorkflowServiceHost = "DEIS_WORKFLOW_SERVICE_HOST"
	deisWorkflowServicePort = "DEIS_WORKFLOW_SERVICE_PORT"
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

func getRandAppName() string {
	return fmt.Sprintf("test-%d", rand.Intn(999999999))
}

func TestTests(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Deis Workflow")
}

var (
	randSuffix        = rand.Intn(1000)
	testUser          = fmt.Sprintf("test-%d", randSuffix)
	testPassword      = "asdf1234"
	testEmail         = fmt.Sprintf("test-%d@deis.io", randSuffix)
	testAdminUser     = "admin"
	testAdminPassword = "admin"
	testAdminEmail    = "admin@example.com"
	keyName           = fmt.Sprintf("deiskey-%v", randSuffix)
	url               = getController()
	debug             = os.Getenv("DEBUG") != ""
	homeHome          = os.Getenv("HOME")
)

var testRoot, testHome, keyPath, gitSSH string

var _ = BeforeSuite(func() {
	SetDefaultEventuallyTimeout(10 * time.Second)

	// use the "deis" executable in the search $PATH
	output, err := exec.LookPath("deis")
	Expect(err).NotTo(HaveOccurred(), output)

	testHome, err = ioutil.TempDir("", "deis-workflow-home")
	Expect(err).NotTo(HaveOccurred())
	os.Setenv("HOME", testHome)

	// register the test-admin user
	registerOrLogin(url, testAdminUser, testAdminPassword, testAdminEmail)

	// verify this user is an admin by running a privileged command
	sess, err := start("deis users:list")
	Expect(err).To(BeNil())
	Eventually(sess).Should(gexec.Exit(0))

	sshDir := path.Join(testHome, ".ssh")

	// register the test user and add a key
	registerOrLogin(url, testUser, testPassword, testEmail)

	keyPath = createKey(keyName)

	gitSSH = path.Join(sshDir, "git-ssh")

	sshFlags := ""
	if debug {
		sshFlags = sshFlags + " -v"
	}

	ioutil.WriteFile(gitSSH, []byte(fmt.Sprintf("#!/bin/sh\nexec /usr/bin/ssh %s -i %s \"$@\"", sshFlags, keyPath)), 0777)

	sess, err = start("deis keys:add %s.pub", keyPath)
	Expect(err).To(BeNil())
	Eventually(sess).Should(gexec.Exit(0))
	Eventually(sess).Should(gbytes.Say("Uploading %s.pub to deis... done", keyName))

	time.Sleep(5 * time.Second) // wait for ssh key to propagate
})

var _ = BeforeEach(func() {
	var err error
	var output string

	testRoot, err = ioutil.TempDir("", "deis-workflow-test")
	Expect(err).NotTo(HaveOccurred())

	os.Chdir(testRoot)
	output, err = execute(`git clone git@github.com:deis/example-go.git .`)
	Expect(err).NotTo(HaveOccurred(), output)

	login(url, testUser, testPassword)
})

var _ = AfterEach(func() {
	err := os.RemoveAll(testRoot)
	Expect(err).NotTo(HaveOccurred())
})

var _ = AfterSuite(func() {
	cancelUserSess, cancelUserErr := cancelSess(url, testUser, testPassword)
	cancelAdminSess, cancelAdminErr := cancelSess(url, testAdminUser, testAdminPassword)

	Expect(cancelUserErr).To(BeNil())
	Expect(cancelAdminErr).To(BeNil())

	cancelUserSess.Wait(10 * time.Second)
	cancelAdminSess.Wait(10 * time.Second)

	os.RemoveAll(fmt.Sprintf("~/.ssh/%s*", keyName))

	err := os.RemoveAll(testHome)
	Expect(err).NotTo(HaveOccurred())

	os.Setenv("HOME", homeHome)
})

func register(url, username, password, email string) {
	sess, err := start("deis register %s --username=%s --password=%s --email=%s", url, username, password, email)
	Expect(err).To(BeNil())
	Eventually(sess).Should(gbytes.Say("Registered %s", username))
	Eventually(sess).Should(gbytes.Say("Logged in as %s", username))
}

func registerOrLogin(url, username, password, email string) {
	sess, err := start("deis register %s --username=%s --password=%s --email=%s", url, username, password, email)

	Expect(err).To(BeNil())

	sess.Wait()

	if strings.Contains(string(sess.Err.Contents()), "must be unique") {
		// Already registered
		login(url, username, password)
	} else {
		Eventually(sess).Should(gexec.Exit(0))
		Eventually(sess).Should(SatisfyAll(
			gbytes.Say("Registered %s", username),
			gbytes.Say("Logged in as %s", username)))
	}
}

func cancelSess(url, user, pass string) (*gexec.Session, error) {
	lgSess, err := loginSess(url, user, pass)
	if err != nil {
		return nil, err
	}
	lgSess.Wait()
	cmd := exec.Command("deis", "auth:cancel", fmt.Sprintf("--username=%s", user), fmt.Sprintf("--password=%s", pass), "--yes")
	return gexec.Start(cmd, GinkgoWriter, GinkgoWriter)
}

func cancel(url, username, password string) {
	// log in to the account
	login(url, username, password)

	// cancel the account
	sess, err := start("deis auth:cancel --username=%s --password=%s --yes", username, password)
	Expect(err).To(BeNil())
	Eventually(sess).Should(gexec.Exit(0))
	Eventually(sess).Should(gbytes.Say("Account cancelled"))
}

func loginSess(url, user, pass string) (*gexec.Session, error) {
	cmd := exec.Command("deis", "login", url, fmt.Sprintf("--username=%s", user), fmt.Sprintf("--password=%s", pass))
	return gexec.Start(cmd, GinkgoWriter, GinkgoWriter)
}

func login(url, user, password string) {
	sess, err := start("deis login %s --username=%s --password=%s", url, user, password)
	Expect(err).To(BeNil())
	Eventually(sess).Should(gexec.Exit(0))
	Eventually(sess).Should(gbytes.Say("Logged in as %s", user))
}

func logout() {
	sess, err := start("deis auth:logout")
	Expect(err).To(BeNil())
	Eventually(sess).Should(gexec.Exit(0))
	Eventually(sess).Should(gbytes.Say("Logged out\n"))
}

// execute executes the command generated by fmt.Sprintf(cmdLine, args...) and returns its output as a cmdOut structure.
// this structure can then be matched upon using the SucceedWithOutput matcher below
func execute(cmdLine string, args ...interface{}) (string, error) {
	var cmd *exec.Cmd
	shCommand := fmt.Sprintf(cmdLine, args...)

	if debug {
		fmt.Println(shCommand)
	}

	cmd = exec.Command("/bin/sh", "-c", shCommand)
	outputBytes, err := cmd.CombinedOutput()

	output := string(outputBytes)

	if debug {
		fmt.Println(output)
	}

	return output, err
}

func start(cmdLine string, args ...interface{}) (*gexec.Session, error) {
	cmdStr := fmt.Sprintf(cmdLine, args...)
	if debug {
		fmt.Println(cmdStr)
	}
	cmd := exec.Command("/bin/sh", "-c", cmdStr)
	return gexec.Start(cmd, GinkgoWriter, GinkgoWriter)
}

func createKey(name string) string {
	keyPath := path.Join(testHome, ".ssh", name)
	os.MkdirAll(path.Join(testHome, ".ssh"), 0777)
	// create the key under ~/.ssh/<name> if it doesn't already exist
	if _, err := os.Stat(keyPath); os.IsNotExist(err) {
		sess, err := start("ssh-keygen -q -t rsa -b 4096 -C %s -f %s -N ''", name, keyPath)
		Expect(err).To(BeNil())
		Eventually(sess).Should(gexec.Exit(0))
	}

	os.Chmod(keyPath, 0600)

	return keyPath
}

func getController() string {
	host := os.Getenv(deisWorkflowServiceHost)
	if host == "" {
		panicStr := fmt.Sprintf(`Set %s to the workflow controller hostname for tests, such as:

$ %s=deis.10.245.1.3.xip.io make test-integration`, deisWorkflowServiceHost, deisWorkflowServiceHost)
		panic(panicStr)
	}
	port := os.Getenv(deisWorkflowServicePort)
	switch port {
	case "443":
		return "https://" + host
	case "80", "":
		return "http://" + host
	default:
		return fmt.Sprintf("http://%s:%s", host, port)
	}
}

func createApp(name string) *gexec.Session {
	cmd, err := start("deis apps:create %s", name)
	Expect(err).NotTo(HaveOccurred())
	Eventually(cmd).Should(gbytes.Say("created %s", name))

	return cmd
}

func destroyApp(name string) *gexec.Session {
	cmd, err := start("deis apps:destroy --app=%s --confirm=%s", name, name)
	Expect(err).NotTo(HaveOccurred())
	Eventually(cmd).Should(gexec.Exit(0))
	Eventually(cmd).Should(SatisfyAll(
		gbytes.Say("Destroying %s...", name),
		gbytes.Say(`done in `)))

	return cmd
}
