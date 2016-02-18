package ps

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

const processesFixture string = `
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "release": "v2",
            "type": "web",
            "name": "example-go-v2-web-45678",
            "state": "up",
            "started": "2016-02-13T00:47:52"
        }
    ]
}`

const restartAllFixture string = `[
    {
        "release": "v2",
        "type": "web",
        "name": "example-go-v2-web-45678",
        "state": "up",
        "started": "2016-02-13T00:47:52"
    }
]
`

const restartWorkerFixture string = `[
    {
        "release": "v2",
        "type": "worker",
        "name": "example-go-v2-worker-45678",
        "state": "up",
        "started": "2016-02-13T00:47:52"
    }
]
`

const restartWebTwoFixture string = `[
    {
        "release": "v2",
        "type": "web",
        "name": "example-go-v2-web-45678",
        "state": "up",
        "started": "2016-02-13T00:47:52"
    }
]
`

const scaleExpected string = `{"web":2}`

type fakeHTTPServer struct{}

func (fakeHTTPServer) ServeHTTP(res http.ResponseWriter, req *http.Request) {
	res.Header().Add("DEIS_API_VERSION", version.APIVersion)

	if req.URL.Path == "/v2/apps/example-go/pods/" && req.Method == "GET" {
		res.Write([]byte(processesFixture))
		return
	}

	if req.URL.Path == "/v2/apps/example-go/pods/restart/" && req.Method == "POST" {
		res.Write([]byte(restartAllFixture))
		return
	}

	if req.URL.Path == "/v2/apps/example-go/pods/web/restart/" && req.Method == "POST" {
		res.Write([]byte(restartWebTwoFixture))
		return
	}

	if req.URL.Path == "/v2/apps/example-go/pods/worker/example-go-v2-worker-45678/restart/" && req.Method == "POST" {
		res.Write([]byte(restartWorkerFixture))
		return
	}

	if req.URL.Path == "/v2/apps/example-go/pods/worker/worker-45678/restart/" && req.Method == "POST" {
		res.Write([]byte(restartWorkerFixture))
		return
	}

	if req.URL.Path == "/v2/apps/example-go/scale/" && req.Method == "POST" {
		body, err := ioutil.ReadAll(req.Body)

		if err != nil {
			fmt.Println(err)
			res.WriteHeader(http.StatusInternalServerError)
			res.Write(nil)
		}

		if string(body) != scaleExpected {
			fmt.Printf("Expected '%s', Got '%s'\n", scaleExpected, body)
			res.WriteHeader(http.StatusInternalServerError)
			res.Write(nil)
			return
		}

		res.WriteHeader(http.StatusNoContent)
		res.Write(nil)
		return
	}

	fmt.Printf("Unrecognized URL %s\n", req.URL)
	res.WriteHeader(http.StatusNotFound)
	res.Write(nil)
}

func TestProcessesList(t *testing.T) {
	t.Parallel()

	started := time.Time{}
	started.UnmarshalText([]byte("2016-02-13T00:47:52"))
	expected := []api.Pods{
		{
			Release: "v2",
			Type:    "web",
			Name:    "example-go-v2-web-45678",
			State:   "up",
			Started: started,
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

	actual, _, err := List(&client, "example-go", 100)

	if err != nil {
		t.Fatal(err)
	}

	if !reflect.DeepEqual(expected, actual) {
		t.Error(fmt.Errorf("Expected %v, Got %v", expected, actual))
	}
}

type testExpected struct {
	Name     string
	Type     string
	Expected []api.Pods
}

func TestAppsRestart(t *testing.T) {
	t.Parallel()

	started := time.Time{}
	started.UnmarshalText([]byte("2016-02-13T00:47:52"))
	tests := []testExpected{
		{
			Name: "",
			Type: "",
			Expected: []api.Pods{
				{
					Release: "v2",
					Type:    "web",
					Name:    "example-go-v2-web-45678",
					State:   "up",
					Started: started,
				},
			},
		},
		{
			Name: "example-go-v2-worker-45678",
			Type: "worker",
			Expected: []api.Pods{
				{
					Release: "v2",
					Type:    "worker",
					Name:    "example-go-v2-worker-45678",
					State:   "up",
					Started: started,
				},
			},
		},
		{
			Name: "worker-45678",
			Type: "worker",
			Expected: []api.Pods{
				{
					Release: "v2",
					Type:    "worker",
					Name:    "example-go-v2-worker-45678",
					State:   "up",
					Started: started,
				},
			},
		},
		{
			Name: "",
			Type: "web",
			Expected: []api.Pods{
				{
					Release: "v2",
					Type:    "web",
					Name:    "example-go-v2-web-45678",
					State:   "up",
					Started: started,
				},
			},
		},
	}

	handler := fakeHTTPServer{}
	server := httptest.NewServer(&handler)
	defer server.Close()

	u, err := url.Parse(server.URL)

	if err != nil {
		t.Fatal(err)
	}

	httpClient := client.CreateHTTPClient(false)

	client := client.Client{HTTPClient: httpClient, ControllerURL: *u, Token: "abc"}

	for _, test := range tests {
		actual, err := Restart(&client, "example-go", test.Type, test.Name)

		if err != nil {
			t.Error(err)
		}

		if !reflect.DeepEqual(test.Expected, actual) {
			t.Error(fmt.Errorf("Expected %v, Got %v", test.Expected, actual))
		}
	}
}

func TestScale(t *testing.T) {
	t.Parallel()

	handler := fakeHTTPServer{}
	server := httptest.NewServer(&handler)
	defer server.Close()

	u, err := url.Parse(server.URL)

	if err != nil {
		t.Fatal(err)
	}

	httpClient := client.CreateHTTPClient(false)

	client := client.Client{HTTPClient: httpClient, ControllerURL: *u, Token: "abc"}

	if err = Scale(&client, "example-go", map[string]int{"web": 2}); err != nil {
		t.Fatal(err)
	}
}
