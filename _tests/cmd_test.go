package _tests_test

import (
	"bytes"
	"errors"
	"fmt"
	"github.com/onsi/gomega"
	"github.com/onsi/gomega/types"
	// "io"
	"os"
	"os/exec"
	"strings"
)

// cmdOut is the output of a command. it's used by cmdMatcher to match on
type cmdOut struct {
	args   []string
	stdout string
	stderr string
	err    error
}

func (c *cmdOut) String() string {
	return strings.Join(c.args, " ")
}

func cmd(cmdLine string, args ...interface{}) *cmdOut {
	var stdout, stderr bytes.Buffer
	var cmd *exec.Cmd
	cmd = exec.Command("/bin/sh", "-c", fmt.Sprintf(cmdLine, args...))
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	cmd.Env = os.Environ()
	ret := &cmdOut{}
	ret.args = cmd.Args
	ret.err = cmd.Run()
	ret.stdout = stdout.String()
	ret.stderr = stderr.String()
	return ret
}

var (
	errExpectedCmdOut = errors.New("cmdMatcher expects a *cmdOut")
)

func cmdErr(co *cmdOut) error {
	return fmt.Errorf("COMMAND ERROR\n[%s]\nError: %s\nSTDOUT: %s\nSTDERR: %s",
		strings.Join(co.args, " "),
		co.err,
		co.stdout,
		co.stderr,
	)
}

// Command
type successfulCmdMatcher struct {
	// will be filled in when Match is called
	cmdo     *cmdOut
	matchers []types.GomegaMatcher
}

// SucceedWithOutput returns a matcher that will match on a *cmdOut, ensuring that the command returned no error
// and its output matches all the given matchers
func BeASuccessfulCmdWithOutput(matchers ...types.GomegaMatcher) types.GomegaMatcher {
	return &successfulCmdMatcher{matchers: matchers}
}

func BeASuccessfulCmd() types.GomegaMatcher {
	return &successfulCmdMatcher{matchers: nil}
}

// Match is the interface implementation of github.com/onsi/gomega/types.GomegaMatcher
func (c *successfulCmdMatcher) Match(actual interface{}) (bool, error) {
	cmdo, ok := actual.(*cmdOut)
	if !ok {
		return false, errExpectedCmdOut
	}
	c.cmdo = cmdo
	if cmdo.err != nil {
		return false, cmdErr(cmdo)
	}
	return gomega.SatisfyAll(c.matchers...).Match(actual)
}

// FailureMessage is the interface implementation of github.com/onsi/gomega/types.GomegaMatcher
func (c *successfulCmdMatcher) FailureMessage(actual interface{}) string {
	if c.cmdo == nil {
		return "command failed, but wasn't recorded"
	}
	return cmdErr(c.cmdo).Error()
}

// NegatedFailureMessage is the interface implementation of github.com/onsi/gomega/types.GomegaMatcher
func (c *successfulCmdMatcher) NegatedFailureMessage(actual interface{}) string {
	if c.cmdo == nil {
		return "command failed, but wasn't recorded"
	}

	return cmdErr(c.cmdo).Error()
}
