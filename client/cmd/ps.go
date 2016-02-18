package cmd

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/deis/workflow/client/controller/api"
	"github.com/deis/workflow/client/controller/models/ps"
)

// PsList lists an app's processes.
func PsList(appID string, results int) error {
	c, appID, err := load(appID)
	if err != nil {
		return err
	}

	if results == defaultLimit {
		results = c.ResponseLimit
	}

	processes, _, err := ps.List(c, appID, results)
	if err != nil {
		return err
	}

	printProcesses(appID, processes)

	return nil
}

// PsScale scales an app's processes.
func PsScale(appID string, targets []string) error {
	c, appID, err := load(appID)

	if err != nil {
		return err
	}

	targetMap := make(map[string]int)
	regex := regexp.MustCompile("^([A-z]+)=([0-9]+)$")

	for _, target := range targets {
		if regex.MatchString(target) {
			captures := regex.FindStringSubmatch(target)
			targetMap[captures[1]], err = strconv.Atoi(captures[2])

			if err != nil {
				return err
			}
		} else {
			fmt.Printf("'%s' does not match the pattern 'type=num', ex: web=2\n", target)
		}
	}

	fmt.Printf("Scaling processes... but first, %s!\n", drinkOfChoice())
	startTime := time.Now()
	quit := progress()

	err = ps.Scale(c, appID, targetMap)

	quit <- true
	<-quit

	if err != nil {
		return err
	}

	fmt.Printf("done in %ds\n", int(time.Since(startTime).Seconds()))

	processes, _, err := ps.List(c, appID, c.ResponseLimit)
	if err != nil {
		return err
	}

	printProcesses(appID, processes)
	return nil
}

// PsRestart restarts an app's processes.
func PsRestart(appID, target string) error {
	c, appID, err := load(appID)

	if err != nil {
		return err
	}

	psType := ""
	psName := ""

	if target != "" {
		if strings.Contains(target, "-") {
			parts := strings.Split(target, "-")
			// the API requires the type, for now
			psType = parts[len(parts)-2]
			// process name is the full pod
			psName = target
		} else {
			psType = target
		}
	}

	fmt.Printf("Restarting processes... but first, %s!\n", drinkOfChoice())
	startTime := time.Now()
	quit := progress()

	processes, err := ps.Restart(c, appID, psType, psName)

	quit <- true
	<-quit

	if err != nil {
		return err
	}

	if len(processes) == 0 {
		fmt.Println("Could not find any processes to restart")
	} else {
		fmt.Printf("done in %ds\n", int(time.Since(startTime).Seconds()))
		printProcesses(appID, processes)
	}

	return nil
}

func printProcesses(appID string, processes []api.Pods) {
	psMap := ps.ByType(processes)

	fmt.Printf("=== %s Processes\n", appID)

	for psType, procs := range psMap {
		fmt.Printf("--- %s:\n", psType)

		for _, proc := range procs {
			fmt.Printf("%s %s (%s)\n", proc.Name, proc.State, proc.Release)
		}
	}
}
