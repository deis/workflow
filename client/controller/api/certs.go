package api

import "github.com/deis/pkg/time"

// Cert is the definition of the cert object.
// Some fields are omtempty because they are only
// returned when creating or getting a cert.
type Cert struct {
	Updated        time.Time `json:"updated,omitempty"`
	Created        time.Time `json:"created,omitempty"`
	Name           string    `json:"name"`
	CommonName     string    `json:"common_name"`
	Expires        time.Time `json:"expires"`
	Starts         time.Time `json:"starts"`
	Fingerprint    string    `json:"fingerprint"`
	Issuer         string    `json:"issuer"`
	Subject        string    `json:"subject"`
	SubjectAltName []string  `json:"san,omitempty"`
	Domains        []string  `json:"domains,omitempty"`
	Owner          string    `json:"owner,omitempty"`
	ID             int       `json:"id,omitempty"`
}

// CertCreateRequest is the definition of POST and PUT to /v2/certs/
type CertCreateRequest struct {
	Certificate string `json:"certificate"`
	Key         string `json:"key"`
	Name        string `json:"name"`
}

// CertAttachRequest is the defintion of post to /v2/certs/<cert>/domain
type CertAttachRequest struct {
	Domain string `json:"domain"`
}
