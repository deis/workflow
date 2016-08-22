# Booting Kubernetes Using Vagrant

This guide will walk you through the process of installing a small development
Kubernetes cluster on your local machine.

## Pre-requisites

1. Install latest version >= 1.7.4 of vagrant from http://www.vagrantup.com/downloads.html
2. Install one of:
   1. The latest version of [Virtual Box](https://www.virtualbox.org/wiki/Downloads)
   2. [VMWare Fusion](https://www.vmware.com/products/fusion/) version 5 or greater as well as the appropriate [Vagrant VMWare Fusion provider](https://www.vagrantup.com/vmware)
   3. [VMWare Workstation](https://www.vmware.com/products/workstation/) version 9 or greater as well as the [Vagrant VMWare Workstation provider](https://www.vagrantup.com/vmware)
   4. [Parallels Desktop](https://www.parallels.com/products/desktop/) version 9 or greater as well as the [Vagrant Parallels provider](https://parallels.github.io/vagrant-parallels/)
3. At least 4GB of RAM for the virtual machines.

## Download and Unpack Kubernetes

First, make a directory to hold the Kubernetes release files:

```
$ mkdir my-first-cluster
$ cd my-first-cluster
```

See [Kubernetes Versions](https://deis.com/docs/workflow/installing-workflow/system-requirements/#kubernetes-versions) under System Requirements and download a Kubernetes release that is compatible with Deis Workflow, and extract the archive on your machine.

This archive has everything that you need to launch Kubernetes. It's a fairly large archive, so it may take some time to download:

```
$ curl -sSL https://storage.googleapis.com/kubernetes-release/release/v1.3.5/kubernetes.tar.gz -O
$ tar -xvzf kubernetes.tar.gz
$ cd kubernetes
$ ls
LICENSES     README.md    Vagrantfile  cluster/     contrib/     docs/        examples/    platforms/   server/      third_party/ version
```

## Configure the Kubernetes Environment

Before calling the Kubernetes setup scripts, we need to change a few defaults so that Deis Workflow works best. Type
each of these commands into your terminal application before calling `kube-up.sh`.

First, use Vagrant as the provider:

```
$ export KUBERNETES_PROVIDER=vagrant
```

For evaluation, we find that the worker nodes need a bit more memory than the default 1GB. We will allocate 1.5GB for
the master node and 4GB for the worker node:

```
export KUBERNETES_MASTER_MEMORY=1536
export KUBERNETES_NODE_MEMORY=4096
```

Double check the configured environment variables:

```
$ env | grep KUBE
KUBE_ENABLE_INSECURE_REGISTRY=true
KUBERNETES_PROVIDER=vagrant
KUBERNETES_NODE_MEMORY=4096
KUBERNETES_MASTER_MEMORY=1536
```

## Boot Your First Cluster

We are now ready to boot our first Kubernetes cluster using Vagrant!

Since this script does a **lot** of stuff, we'll break it into sections.

```
kubernetes $ ./cluster/kube-up.sh
... Starting cluster using provider: vagrant
... calling verify-prereqs
... calling kube-up
Bringing machine 'master' up with 'virtualbox' provider...
Bringing machine 'node-1' up with 'virtualbox' provider...
==> master: Box 'kube-fedora23' could not be found. Attempting to find and install...

...REDACTED...

```

Two machines have been created via vagrant, `master` and `node-1`. The step downloads a load of packages and sets up
Kubernetes so it can take some time.

```
cluster "vagrant" set.
user "vagrant" set.
context "vagrant" set.
switched to context "vagrant".
user "vagrant-basic-auth" set.
Wrote config for vagrant to /Users/jhansen/.kube/config
Each machine instance has been created/updated.
  Now waiting for the Salt provisioning process to complete on each machine.
  This can take some time based on your network, disk, and cpu speed.
  It is possible for an error to occur during Salt provision of cluster and this could loop forever.
Validating master
Validating node-1
```

Now that the master is up and ready, `kube-up.sh` automatically configures `kubectl` on your machine with appropriate
authentication and endpoint information.

```
Kubernetes cluster is running.

The master is running at:

  https://10.245.1.2

Administer and visualize its resources using Cockpit:

  https://10.245.1.2:9090

For more information on Cockpit, visit http://cockpit-project.org

The user name and password to use is located in /Users/jhansen/.kube/config

... calling validate-cluster
Found 1 node(s).
NAME                STATUS    AGE
kubernetes-node-1   Ready     1m
Flag --api-version has been deprecated, flag is no longer respected and will be deleted in the next release
Validate output:
NAME                 STATUS    MESSAGE              ERROR
controller-manager   Healthy   ok
scheduler            Healthy   ok
etcd-1               Healthy   {"health": "true"}
etcd-0               Healthy   {"health": "true"}
Cluster validation succeeded
Done, listing cluster services:

Kubernetes master is running at https://10.245.1.2
Heapster is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/heapster
KubeDNS is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kube-dns
kubernetes-dashboard is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard
Grafana is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-grafana
InfluxDB is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-influxdb
```

You are now ready to [install Deis Workflow](install-vagrant.md)
