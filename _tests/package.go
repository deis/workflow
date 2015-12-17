// Package _tests contains integration tests for the Deis open source PaaS.
package _tests

import (
	"github.com/onsi/ginkgo/config"
	"math/rand"
)

func init() {
	rand.Seed(config.GinkgoConfig.RandomSeed)
}
