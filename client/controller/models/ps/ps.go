package ps

import (
	"encoding/json"
	"fmt"

	"github.com/deis/workflow/client/controller/api"
	"github.com/deis/workflow/client/controller/client"
)

// List an app's processes.
func List(c *client.Client, appID string, results int) ([]api.Pods, int, error) {
	u := fmt.Sprintf("/v2/apps/%s/pods/", appID)
	body, count, err := c.LimitedRequest(u, results)
	if err != nil {
		return []api.Pods{}, -1, err
	}

	var procs []api.Pods
	if err = json.Unmarshal([]byte(body), &procs); err != nil {
		return []api.Pods{}, -1, err
	}

	return procs, count, nil
}

// Scale an app's processes.
func Scale(c *client.Client, appID string, targets map[string]int) error {
	u := fmt.Sprintf("/v2/apps/%s/scale/", appID)

	body, err := json.Marshal(targets)

	if err != nil {
		return err
	}

	_, err = c.BasicRequest("POST", u, body)
	return err
}

// Restart an app's processes.
func Restart(c *client.Client, appID string, procType string, name string) ([]api.Pods, error) {
	u := fmt.Sprintf("/v2/apps/%s/pods/", appID)

	if procType == "" {
		u += "restart/"
	} else {
		if name == "" {
			u += procType + "/restart/"
		} else {
			u += procType + "/" + name + "/restart/"
		}
	}

	body, err := c.BasicRequest("POST", u, nil)

	if err != nil {
		return []api.Pods{}, err
	}

	procs := []api.Pods{}
	if err = json.Unmarshal([]byte(body), &procs); err != nil {
		return []api.Pods{}, err
	}

	return procs, nil
}

// ByType organizes processes of an app by process type.
func ByType(processes []api.Pods) map[string][]api.Pods {
	psMap := make(map[string][]api.Pods)

	for _, ps := range processes {
		psMap[ps.Type] = append(psMap[ps.Type], ps)
	}

	return psMap
}
