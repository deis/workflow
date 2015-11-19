# Quick Start

These steps will help you provision a Deis cluster.

## Check System Requirements

The Deis provision scripts default to a machine size which should be adequate to run Deis, but this can be customized. Please refer to the [system requirements][] for resource considerations when choosing a machine size to run Deis.

## Choose a Provider

Choose one of the following providers and deploy a new cluster:

- [Amazon AWS](http://kubernetes.io/v1.1/docs/getting-started-guides/aws.html)
- [Bare Metal](bare-metal.md)
- [DigitalOcean](digitalocean.md)
- [Google Compute Engine](http://kubernetes.io/v1.1/docs/getting-started-guides/gce.html)
- [Microsoft Azure](http://kubernetes.io/v1.1/docs/getting-started-guides/azure.html)
- [Vagrant](http://kubernetes.io/v1.1/docs/getting-started-guides/vagrant.html)

## Configure DNS

See [Configuring DNS][] for more information on properly setting up your DNS records with Deis.

## Install Deis Platform

Now that you've finished provisioning a cluster, please [Install the Deis Platform][install deis].


[configuring dns]: ../managing-deis/configuring-dns.md
[install deis]: installing-the-deis-platform.md
[system requirements]: system-requirements.md
