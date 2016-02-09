package certs

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"reflect"
	"testing"

	"github.com/deis/pkg/time"
	"github.com/deis/workflow/client/controller/api"
	"github.com/deis/workflow/client/controller/client"
	"github.com/deis/workflow/client/version"
)

const certsFixture string = `
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
			"name": "test-example-com",
            "common_name": "test.example.com",
            "expires": "2014-01-01T00:00:00UTC",
			"fingerprint": "12:34:56:78:90"
        }
    ]
}`

const certFixture string = `
{
    "updated": "2014-01-01T00:00:00UTC",
    "created": "2014-01-01T00:00:00UTC",
    "expires": "2015-01-01T00:00:00UTC",
	"starts": "2014-01-01T00:00:00UTC",
	"fingerprint": "12:34:56:78:90",
	"name": "test-example-com",
    "owner": "test",
    "id": 1
}`

const certExpected string = `{"certificate":"test","key":"foo","name":"test-example-com"}`

type fakeHTTPServer struct{}

func (fakeHTTPServer) ServeHTTP(res http.ResponseWriter, req *http.Request) {
	res.Header().Add("DEIS_API_VERSION", version.APIVersion)

	if req.URL.Path == "/v2/certs/" && req.Method == "GET" {
		res.Write([]byte(certsFixture))
		return
	}

	if req.URL.Path == "/v2/certs/test-example-com" && req.Method == "GET" {
		res.Write([]byte(certFixture))
		return
	}

	if req.URL.Path == "/v2/certs/" && req.Method == "POST" {
		body, err := ioutil.ReadAll(req.Body)

		if err != nil {
			fmt.Println(err)
			res.WriteHeader(http.StatusInternalServerError)
			res.Write(nil)
		}

		if string(body) != certExpected {
			fmt.Printf("Expected '%s', Got '%s'\n", certExpected, body)
			res.WriteHeader(http.StatusInternalServerError)
			res.Write(nil)
			return
		}
		res.WriteHeader(http.StatusCreated)
		res.Write([]byte(certFixture))
		return
	}

	if req.URL.Path == "/v2/certs/test-example-com/domain/" && req.Method == "POST" {
		res.WriteHeader(http.StatusCreated)
		res.Write(nil)
		return
	}

	if req.URL.Path == "/v2/certs/test-example-com" && req.Method == "DELETE" {
		res.WriteHeader(http.StatusNoContent)
		res.Write(nil)
		return
	}

	if req.URL.Path == "/v2/certs/test-example-com/domain/foo.com" && req.Method == "DELETE" {
		res.WriteHeader(http.StatusNoContent)
		res.Write(nil)
		return
	}

	fmt.Printf("Unrecognized URL %s\n", req.URL)
	res.WriteHeader(http.StatusNotFound)
	res.Write(nil)
}

func TestCertsList(t *testing.T) {
	t.Parallel()

	expires := time.Time{}

	if err := expires.UnmarshalText([]byte("2014-01-01T00:00:00UTC")); err != nil {
		t.Fatalf("could not unmarshal time (%s)", err)
	}

	expected := []api.Cert{
		{
			Name:        "test-example-com",
			Expires:     expires,
			CommonName:  "test.example.com",
			Fingerprint: "12:34:56:78:90",
		},
	}

	handler := fakeHTTPServer{}
	server := httptest.NewServer(handler)
	defer server.Close()

	u, err := url.Parse(server.URL)

	if err != nil {
		t.Fatal(err)
	}

	httpClient := client.CreateHTTPClient(false)

	client := client.Client{HTTPClient: httpClient, ControllerURL: *u, Token: "abc"}

	actual, _, err := List(&client, 100)

	if err != nil {
		t.Fatal(err)
	}

	if !reflect.DeepEqual(expected, actual) {
		t.Errorf("Expected %v, Got %v", expected, actual)
	}
}

func TestCert(t *testing.T) {
	t.Parallel()

	created := time.Time{}
	created.UnmarshalText([]byte("2014-01-01T00:00:00UTC"))
	expires := time.Time{}
	expires.UnmarshalText([]byte("2015-01-01T00:00:00UTC"))

	expected := api.Cert{
		Updated:     created,
		Created:     created,
		Starts:      created,
		Expires:     expires,
		Fingerprint: "12:34:56:78:90",
		Name:        "test-example-com",
		Owner:       "test",
		ID:          1,
	}

	handler := fakeHTTPServer{}
	server := httptest.NewServer(handler)
	defer server.Close()

	u, err := url.Parse(server.URL)

	if err != nil {
		t.Fatal(err)
	}

	httpClient := client.CreateHTTPClient(false)

	client := client.Client{HTTPClient: httpClient, ControllerURL: *u, Token: "abc"}

	actual, err := New(&client, "test", "foo", "test-example-com")

	if err != nil {
		t.Fatal(err)
	}

	if !reflect.DeepEqual(expected, actual) {
		t.Errorf("Expected %v, Got %v", expected, actual)
	}
}

func TestCertInfo(t *testing.T) {
	t.Parallel()

	created := time.Time{}
	created.UnmarshalText([]byte("2014-01-01T00:00:00UTC"))
	expires := time.Time{}
	expires.UnmarshalText([]byte("2015-01-01T00:00:00UTC"))

	expected := api.Cert{
		Updated:     created,
		Created:     created,
		Starts:      created,
		Expires:     expires,
		Fingerprint: "12:34:56:78:90",
		Name:        "test-example-com",
		Owner:       "test",
		ID:          1,
	}

	handler := fakeHTTPServer{}
	server := httptest.NewServer(handler)
	defer server.Close()

	u, err := url.Parse(server.URL)
	if err != nil {
		t.Fatal(err)
	}

	httpClient := client.CreateHTTPClient(false)
	client := client.Client{HTTPClient: httpClient, ControllerURL: *u, Token: "abc"}
	actual, err := Get(&client, "test-example-com")
	if err != nil {
		t.Fatal(err)
	}

	if !reflect.DeepEqual(expected, actual) {
		t.Errorf("Expected %v, Got %v", expected, actual)
	}
}

func TestCertDeleteion(t *testing.T) {
	t.Parallel()

	handler := fakeHTTPServer{}
	server := httptest.NewServer(handler)
	defer server.Close()

	u, err := url.Parse(server.URL)

	if err != nil {
		t.Fatal(err)
	}

	httpClient := client.CreateHTTPClient(false)

	client := client.Client{HTTPClient: httpClient, ControllerURL: *u, Token: "abc"}

	if err = Delete(&client, "test-example-com"); err != nil {
		t.Fatal(err)
	}
}

func TestCertAttach(t *testing.T) {
	t.Parallel()

	handler := fakeHTTPServer{}
	server := httptest.NewServer(handler)
	defer server.Close()

	u, err := url.Parse(server.URL)

	if err != nil {
		t.Fatal(err)
	}

	httpClient := client.CreateHTTPClient(false)

	client := client.Client{HTTPClient: httpClient, ControllerURL: *u, Token: "abc"}

	if err = Attach(&client, "test-example-com", "foo.com"); err != nil {
		t.Fatal(err)
	}
}

func TestCertDetach(t *testing.T) {
	t.Parallel()

	handler := fakeHTTPServer{}
	server := httptest.NewServer(handler)
	defer server.Close()

	u, err := url.Parse(server.URL)

	if err != nil {
		t.Fatal(err)
	}

	httpClient := client.CreateHTTPClient(false)

	client := client.Client{HTTPClient: httpClient, ControllerURL: *u, Token: "abc"}

	if err = Detach(&client, "test-example-com", "foo.com"); err != nil {
		t.Fatal(err)
	}
}
