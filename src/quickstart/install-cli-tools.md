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
    v2.11.0

!!! note
    Note that version numbers may vary as new releases become available

## Helm Installation

We will install Deis Workflow using Helm which is a tool for installing and managing software in a
Kubernetes cluster.

Install the latest `helm` cli for Linux or Mac OS X by following the
[installation instructions][helm-install].

## Step 2: Boot a Kubernetes Cluster and Install Deis Workflow

There are many ways to boot and run Kubernetes. You may choose to get up and running in cloud environments or locally on your laptop.

Cloud-based options:

* [Google Container Engine](provider/gke/boot.md): provides a managed Kubernetes environment, available with a few clicks.
* [Amazon Web Services](provider/aws/boot.md): uses Kubernetes upstream `kube-up.sh` to boot a cluster on AWS EC2.
* [Azure Container Service](provider/azure-acs/boot.md): provides a managed Kubernetes environment.

If you would like to test on your local machine follow our guide for [Vagrant](provider/vagrant/boot.md).


[helm-install]: https://github.com/kubernetes/helm#install
