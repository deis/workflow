package _tests_test

import (
	"fmt"
	"math/rand"

	"github.com/onsi/ginkgo/config"
)

func init() {
	rand.Seed(config.GinkgoConfig.RandomSeed)
}

func getRandAppName() string {
	return fmt.Sprintf("apps-test-%d", rand.Int())
}
