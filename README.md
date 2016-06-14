![](https://deis.com/images/deis-logo.png)

[![Slack Status](https://slack.deis.io/badge.svg)](https://slack.deis.io/)

**Deis Workflow** is an open source Platform as a Service (PaaS) that adds a developer-friendly layer to any [Kubernetes][k8s-home] cluster, making it easy to deploy and manage applications.

Deis Workflow is the second major release (v2) of the Deis PaaS. If you are looking for the CoreOS-based PaaS visit [https://github.com/deis/deis](https://github.com/deis/deis).

To **get started** with **Deis Workflow** please read the [Quick Start Guide](https://deis.com/docs/workflow/quickstart/).

Visit [https://deis.com](https://deis.com) for more information on [why you should use Deis Workflow](https://deis.com/why-deis/) or [learn about its features](https://deis.com/how-it-works/).

This repository contains the source code for Deis Workflow documentation. If you're looking for individual components, they live in their own repositories.

Please see below for links and descriptions of each component:

- [controller](https://github.com/deis/controller) - Workflow API server
- [builder](https://github.com/deis/builder) - Git server and source-to-image component
- [dockerbuilder](https://github.com/deis/dockerbuilder) - The builder for [Docker](https://www.docker.com/) based applications
- [slugbuilder](https://github.com/deis/slugbuilder) - The builder for [slug/buildpack](https://devcenter.heroku.com/articles/slug-compiler) based applications
- [slugrunner](https://github.com/deis/slugrunner) - The runner for slug/buildpack based applications
- [fluentd](https://github.com/deis/fluentd) - Backend log shipping mechanism for `deis logs`
- [postgres](https://github.com/deis/postgres) - The central database
- [registry](https://github.com/deis/registry) - The Docker registry
- [logger](https://github.com/deis/logger) - The (in-memory) log buffer for `deis logs`
- [monitor](https://github.com/deis/monitor) - The platform monitoring components
- [router](https://github.com/deis/router) - The HTTP/s edge router
- [minio](https://github.com/deis/minio) - The in-cluster, ephemeral, development-only object storage system
- [workflow-cli](https://github.com/deis/workflow-cli) - Workflow CLI `deis`
- [workflow-e2e](https://github.com/deis/workflow-e2e) - End-to-end tests for the entire platform

We welcome your input! If you have feedback, please [submit an issue][issues]. If you'd like to participate in development, please read the "Working on Documentation" section below and [submit a pull request][prs].

# Working on Documentation

[![Build Status](https://travis-ci.org/deis/workflow.svg?branch=master)](https://travis-ci.org/deis/workflow)
[![Latest Docs](http://img.shields.io/badge/docs-latest-fc1e5e.svg)](http://docs-v2.readthedocs.org/en/latest/)

The Deis project welcomes contributions from all developers. The high level process for development matches many other open source projects. See below for an outline.

* Fork this repository
* Make your changes
* [Submit a pull request][prs] (PR) to this repository with your changes, and unit tests whenever possible
	* If your PR fixes any [issues][issues], make sure you write `Fixes #1234` in your PR description (where `#1234` is the number of the issue you're closing)
* The Deis core contributors will review your code. After each of them sign off on your code, they'll label your PR with `LGTM1` and `LGTM2` (respectively). Once that happens, a contributor will merge it

## Requirements

The documentation site requires either a local installation of [MkDocs][] or access to Docker.

### Local Installation

Install [MkDocs][] and required dependencies:

```
make deps
```

## Building Documentation

To build the documentation run: `make build` or `make docker-build`

## Serve Documentation Locally

To serve documenation run: `make serve` or `make docker-serve`

Then view the documentation on [http://localhost:8000](http://localhost:8000) or `http://DOCKER_IP:8000`.

## License

Copyright 2013, 2014, 2015 Engine Yard, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

[k8s-home]: http://kubernetes.io
[install-k8s]: http://kubernetes.io/gettingstarted/
[mkdocs]: http://www.mkdocs.org/
[issues]: https://github.com/deis/workflow/issues
[prs]: https://github.com/deis/workflow/pulls
