# Quick Start

These steps will help you provision a Deis cluster.

## Check System Requirements

Please refer to the [system requirements][] for resource considerations when choosing a machine size to run Deis.

## Choose a Provider

Choose one of the following providers and deploy a new kubernetes cluster:

- [Amazon AWS](http://kubernetes.io/v1.1/docs/getting-started-guides/aws.html)
- [Google Container Engine](https://cloud.google.com/container-engine/docs/before-you-begin)
- [Vagrant](http://kubernetes.io/v1.1/docs/getting-started-guides/vagrant.html)

Reference [this table](http://kubernetes.io/v1.1/docs/getting-started-guides/#table-of-solutions) in the official Kubernetes documentation for a more extensive (but still non-exhaustive) list of Kubernetes provisioning options supported by the project or the community.

## Prerequisites
Please make sure you enable the Daemon Sets api if you are installing a pre-1.2 version of kubernetes. As it is not turned on by default. You can learn more about how to do that [here](http://kubernetes.io/v1.1/docs/api.html#enabling-resources-in-the-extensions-group).

For example, with a CoreOS kubernetes cluster you can edit the api server unit file and add the following line to the `ExecStart` stanza: `--runtime_config=extensions/v1beta1=true,extensions/v1beta1/daemonsets=true`.

Restart your api server and check that the extensions api is enabled:

```
$ kubectl api-versions
$ extensions/v1beta1
```

## Install Deis Platform

Now that you've finished provisioning a cluster, please [Install the Deis Platform][install deis].

## Configure DNS

See [Configuring DNS][] for more information on properly setting up your DNS records with Deis.

## Register a User

Once your cluster has been provisioned and the Deis Platform has been installed, you can
[install the client][client] and [register your first user][register]!


[client]: ../using-deis/installing-the-client.md
[configuring object storage]: configuring-object-storage.md
[configuring dns]: ../managing-deis/configuring-dns.md
[install deis]: installing-the-deis-platform.md
[register]: ../using-deis/registering-a-user.md
[system requirements]: system-requirements.md
