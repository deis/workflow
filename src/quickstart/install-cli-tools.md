## Deis Workflow Client CLI

The Deis command-line interface (CLI), lets you interact with Deis Workflow.
Use the CLI to create and configure and manage applications.

Install the latest `deis` client for Linux or Mac OS X with:

    $ curl -sSL http://deis.io/deis-cli/install-v2.sh | bash

The installer places the `deis` binary in your current directory, but you
should move it somewhere in your $PATH:

    $ sudo ln -fs $PWD/deis /usr/local/bin/deis

*or*:

    $ sudo mv $PWD/deis /usr/local/bin/deis

Check your work by running `deis version`:

    $ deis version
    2.7.0

!!! note
    Note that version numbers may vary as new releases become available

## Helm Classic Installation

We will install Deis Workflow using Helm Classic which is a tool for installing and managing software in a Kubernetes cluster.

Install the latest `helmc` cli for Linux or Mac OS X with:

    $ curl -sSL https://get.helm.sh | bash

!!! note
    Note that the `unzip` package is a requirement for this command

The installer places the `helmc` binary in your current directory, but you
should move it somewhere in your $PATH:

    $ sudo ln -fs $PWD/helmc /usr/local/bin/helmc

*or*:

    $ sudo mv $PWD/helmc /usr/local/bin/helmc

Check your work by running `helmc --version`:

    $ helmc --version
    helmc version 0.8.1+a9c55cf

Make sure you are running at least version 0.8.1 or newer.

## Step 2: Boot a Kubernetes Cluster and Install Deis Workflow

There are many ways to boot and run Kubernetes. You may choose to get up and running in cloud environments or locally on
your laptop.

Cloud-based options:

* [Google Container Engine](provider/gke/boot.md): provides a managed Kubernetes environment, available with a few clicks.
* [Amazon Web Services](provider/aws/boot.md): uses Kubernetes upstream `kube-up.sh` to boot a cluster on AWS EC2.

If you would like to test on your local machine follow our guide for [Vagrant](provider/vagrant/boot.md).
