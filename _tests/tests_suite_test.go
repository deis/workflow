package _tests_test

import (
	"bytes"
	"fmt"
	"math/rand"
	"os"
	"os/exec"
	"os/user"
	"path"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/ginkgo/config"

	. "github.com/onsi/gomega"

	"testing"
)

func init() {
	rand.Seed(GinkgoConfig.RandomSeed)
}

func getRandAppName() string {
	return fmt.Sprintf("apps-test-%d", rand.Int())
}

func TestTests(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests Suite")
}

var (
	testAdminUser     = fmt.Sprintf("test-admin-%d", GinkgoConfig.RandomSeed)
	testAdminPassword = "asdf1234"
	testAdminEmail    = fmt.Sprintf("test-admin-%d@deis.io", GinkgoConfig.RandomSeed)
	testUser          = fmt.Sprintf("test-%d", GinkgoConfig.RandomSeed)
	testPassword      = "asdf1234"
	testEmail         = fmt.Sprintf("test-%d@deis.io", GinkgoConfig.RandomSeed)
	url               = getController()
)

var _ = BeforeSuite(func() {
	// use the "deis" executable in the search $PATH
	_, err := exec.LookPath("deis")
	Expect(err).NotTo(HaveOccurred())

	// register the test-admin user
	register(url, testAdminUser, testAdminPassword, testAdminEmail)
	// TODO: verify that this user is actually an admin

	// register the test user and add a key
	register(url, testUser, testPassword, testEmail)
	addKey("deis-test")
})

var _ = AfterSuite(func() {
	// cancel the test user
	cancel(url, testUser, testPassword)

	// cancel the test-admin user
	cancel(url, testAdminUser, testAdminPassword)
})

func register(url, username, password, email string) {
	cmd := "deis register %s --username=%s --password=%s --email=%s"
	output, err := execute(cmd, url, username, password, email)
	Expect(err).NotTo(HaveOccurred())
	Expect(output).To(SatisfyAll(
		ContainSubstring("Registered %s", username),
		ContainSubstring("Logged in as %s", username)))
}

func cancel(url, username, password string) {
	// log in to the account
	login(url, username, password)

	// cancel the account
	cmd := "deis auth:cancel --username=%s --password=%s --yes"
	output, err := execute(cmd, username, password)
	Expect(err).NotTo(HaveOccurred())
	Expect(output).To(ContainSubstring("Account cancelled"))
}

func login(url, user, password string) {
	cmd := "deis login %s --username=%s --password=%s"
	output, err := execute(cmd, url, user, password)
	Expect(err).NotTo(HaveOccurred())
	Expect(output).To(ContainSubstring("Logged in as %s", user))
}

func logout() {
	output, err := execute("deis auth:logout")
	Expect(err).NotTo(HaveOccurred())
	Expect(output).To(Equal("Logged out\n"))
}

func execute(cmdLine string, args ...interface{}) (string, error) {
	var stdout, stderr bytes.Buffer
	var cmd *exec.Cmd
	cmd = exec.Command("/bin/sh", "-c", fmt.Sprintf(cmdLine, args...))
	cmd.Stdout, cmd.Stderr = &stdout, &stderr
	if err := cmd.Run(); err != nil {
		return stderr.String(), err
	}
	return stdout.String(), nil
}

func addKey(name string) {
	var home string
	if user, err := user.Current(); err != nil {
		home = "~"
	} else {
		home = user.HomeDir
	}
	path := path.Join(home, ".ssh", name)
	// create the key under ~/.ssh/<name> if it doesn't already exist
	if _, err := os.Stat(path); os.IsNotExist(err) {
		cmd := "ssh-keygen -q -t rsa -b 4096 -C otto.test@deis.com -f %s -N ''"
		_, err := execute(cmd, path)
		Expect(err).NotTo(HaveOccurred())
	}
	// add the key to ssh-agent
	_, err := execute("eval $(ssh-agent) && ssh-add %s", path)
	Expect(err).NotTo(HaveOccurred())
	// add the public key to deis (assumes the user is logged in)
	_, err = execute("deis keys:add %s.pub", path)
	Expect(err).NotTo(HaveOccurred())
}

func getController() string {
	host := os.Getenv("DEIS_HOST")
	if host == "" {
		panic(`Set DEIS_HOST to the workflow controller hostname for tests, such as:

$ DEIS_HOST=deis.10.245.1.3.xip.io make test-integration`)
	}
	port := os.Getenv("DEIS_PORT")
	switch port {
	case "443":
		return "https://" + host
	case "80", "":
		return "http://" + host
	default:
		return fmt.Sprintf("http://%s:%s", host, port)
	}
}
