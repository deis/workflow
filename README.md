# Deis Workflow v2

[![Build Status](https://travis-ci.org/deis/workflow.svg?branch=master)](https://travis-ci.org/deis/workflow) [![Go Report Card](http://goreportcard.com/badge/deis/workflow)](http://goreportcard.com/report/deis/workflow)

Deis (pronounced DAY-iss) is an open source PaaS that makes it easy to deploy and manage
applications on your own servers. Deis builds on [Kubernetes](http://kubernetes.io/) to provide
a lightweight, [Heroku-inspired](http://heroku.com) workflow.

## Work in Progress

![Deis Graphic](https://s3-us-west-2.amazonaws.com/get-deis/deis-graphic-small.png)

Deis Workflow v2 is currently in alpha. Your feedback and participation are more than welcome, but be
aware that this project is considered a work in progress.

The following features are not ready in Alpha1, but will be coming
soon.

- Complete SSL support
- Dockerfile builds
- Backup and restore features
- Persistent storage (though it can be manually configured)

## Hacking Workflow

First, install [helm](http://helm.sh) and [boot up a kubernetes cluster][install-k8s]. Next, add the
deis repository to your chart list:

```console
$ helm repo add deis https://github.com/deis/charts
```

Then, install Deis!

```console
$ helm install deis/deis
```

Complete instructions for installing and managing a Deis cluster are
available in the [docs folder](https://github.com/deis/workflow/tree/master/docs/src).


If you want to retrieve the latest client build, check
[the latest builds on Travis CI](https://travis-ci.org/deis/workflow/builds), notice the last build
number that went green and use the following URL to retrieve the client build:

    <https://get-deis.s3.amazonaws.com/deis/workflow/$BUILD_NUM/$BUILD_NUM.1/client/deis>

Note that this client build will only work on Linux. If you're on OS X, you'll have to build the
client from source.

If you want to hack on a new feature, build the deis/workflow image and push it to a Docker
registry. The `$DEIS_REGISTRY` environment variable must point to a registry accessible to your
Kubernetes cluster. You may need to configure the Docker engines on your Kubernetes nodes to allow
`--insecure-registry 192.168.0.0/16` (or the appropriate address range).

```console
$ make docker-build docker-push
```

You'll want to modify the deis chart to use your custom image, then run `helm install` on the
chart.

## License

Copyright 2013, 2014, 2015 Engine Yard, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.


[install-k8s]: http://kubernetes.io/gettingstarted/
