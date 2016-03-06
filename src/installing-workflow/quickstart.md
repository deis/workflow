# Quick Start

These steps will help you install and configure Deis Workflow on a Kubernetes cluster.

## Check System Requirements

Please refer to the prerequisites and [system requirements][] for considerations when planning your Kubernetes environment.

## Choose a Provider

Choose one of the following providers and deploy a new Kubernetes cluster:

- [Amazon AWS](http://kubernetes.io/v1.1/docs/getting-started-guides/aws.html)
- [Google Container Engine](https://cloud.google.com/container-engine/docs/before-you-begin)
- [Vagrant](http://kubernetes.io/v1.1/docs/getting-started-guides/vagrant.html)

Reference [this table](http://kubernetes.io/v1.1/docs/getting-started-guides/#table-of-solutions) in the official Kubernetes documentation for a more extensive (but still non-exhaustive) list of Kubernetes provisioning options supported by the project or the community.

## Install Deis Workflow

Now that you've finished provisioning a cluster, please [Install Deis Workflow][install workflow].

## Configure DNS

See [Configuring DNS][] for more information on properly setting up your DNS records with Deis.

## Register a User

Once your cluster has been provisioned and Deis Workflow has been installed, you can
[install the client][client] and [register your first user][register]!

## Deploy your first Application

Last but not least, select your build process and [deploy your first application][deploy].

[client]: ../using-workflow/installing-the-client.md
[configuring object storage]: configuring-object-storage.md
[configuring dns]: ../managing-workflow/configuring-dns.md
[deploy]: ../using-workflow/deploying-an-application.md
[install workflow]: installing-deis-workflow.md
[register]: ../using-workflow/registering-a-user.md
[system requirements]: system-requirements.md
