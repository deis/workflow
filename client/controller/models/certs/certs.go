package certs

import (
	"encoding/json"
	"fmt"

	"github.com/deis/workflow/client/controller/api"
	"github.com/deis/workflow/client/controller/client"
)

// List certs registered with the controller.
func List(c *client.Client, results int) ([]api.Cert, int, error) {
	body, count, err := c.LimitedRequest("/v2/certs/", results)

	if err != nil {
		return []api.Cert{}, -1, err
	}

	var res []api.Cert
	if err = json.Unmarshal([]byte(body), &res); err != nil {
		return []api.Cert{}, -1, err
	}

	return res, count, nil
}

// New creates a cert.
func New(c *client.Client, cert string, key string, name string) (api.Cert, error) {
	req := api.CertCreateRequest{Certificate: cert, Key: key, Name: name}
	reqBody, err := json.Marshal(req)
	if err != nil {
		return api.Cert{}, err
	}

	resBody, err := c.BasicRequest("POST", "/v2/certs/", reqBody)
	if err != nil {
		return api.Cert{}, err
	}

	resCert := api.Cert{}
	if err = json.Unmarshal([]byte(resBody), &resCert); err != nil {
		return api.Cert{}, err
	}

	return resCert, nil
}

// Get information for a certificate
func Get(c *client.Client, name string) (api.Cert, error) {
	url := fmt.Sprintf("/v2/certs/%s", name)
	body, err := c.BasicRequest("GET", url, nil)
	if err != nil {
		return api.Cert{}, err
	}

	res := api.Cert{}
	if err = json.Unmarshal([]byte(body), &res); err != nil {
		return api.Cert{}, err
	}

	return res, nil
}

// Delete removes a cert.
func Delete(c *client.Client, name string) error {
	url := fmt.Sprintf("/v2/certs/%s", name)
	_, err := c.BasicRequest("DELETE", url, nil)
	return err
}

// Attach a certificate to a domain
func Attach(c *client.Client, name string, domain string) error {
	req := api.CertAttachRequest{Domain: domain}
	reqBody, err := json.Marshal(req)
	if err != nil {
		return err
	}

	url := fmt.Sprintf("/v2/certs/%s/domain/", name)
	_, err = c.BasicRequest("POST", url, reqBody)
	return err
}

// Detach a certificate from a domain
func Detach(c *client.Client, name string, domain string) error {
	url := fmt.Sprintf("/v2/certs/%s/domain/%s", name, domain)
	_, err := c.BasicRequest("DELETE", url, nil)
	return err
}
