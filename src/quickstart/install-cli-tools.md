## Deis Workflow Client CLI

The Deis command-line interface (CLI), lets you interact with Deis Workflow.
Use the CLI to create and configure and manage applications.

Install the latest `deis` client for Linux or Mac OS X with:

    $ curl -sSL http://deis.io/deis-cli/install-v2.sh | bash

The installer places the `deis` binary in your current directory, but you
should move it somewhere in your $PATH:

    $ ln -fs $PWD/deis /usr/local/bin/deis

Check your work by running `deis version`:

    $ deis version
    2.0.0-betaX

## Helm Classic Installation

We will install Deis Workflow using Helm Classic which is a tool for installing and managing software in a Kubernetes cluster.

Install the latest `helm` cli for Linux or Mac OS X with:

    $ curl -sSL https://get.helm.sh | bash

*or*:

1. Grab a prebuilt binary from:
  - the latest release: [ ![Download](https://api.bintray.com/packages/deis/helm/helm/images/download.svg) ](https://bintray.com/deis/helm/helm/_latestVersion#files)
  - the CI build pipeline: [ ![Download](https://api.bintray.com/packages/deis/helm-ci/helm/images/download.svg) ](https://bintray.com/deis/helm-ci/helm/_latestVersion#files)
2. Unzip the package and make sure `helm` is available on the PATH.

Check your work by running `helmc version`:

    $ helmc version
    helmc version 0.7.0+20a7ed7

Make sure you are running at least version 0.7.0 or newer.

## Step 2: Boot a Kubernetes Cluster and Install Deis Workflow

There are many ways to boot and run Kubernetes. You may choose to get up and running in cloud environments or locally on
your laptop.

Cloud-based options:

* [Google Container Engine](provider/gke/boot.md): provides a managed Kubernetes environment, available with a few clicks.
* [Amazon Web Services](provider/aws/boot.md): uses Kubernetes upstream `kube-up.sh` to boot a cluster on AWS EC2.

If you would like to test on your local machine follow our guide for [Vagrant](provider/vagrant/boot.md).
