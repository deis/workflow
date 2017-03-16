# Booting Kubernetes Using Minikube

This guide will walk you through the process of installing a small development
Kubernetes cluster on your local machine using [minikube](https://github.com/kubernetes/minikube).

## Pre-requisites

* OS X
    * [xhyve driver](https://github.com/kubernetes/minikube/blob/master/DRIVERS.md#xhyve-driver), [VirtualBox](https://www.virtualbox.org/wiki/Downloads) or [VMware Fusion](https://www.vmware.com/products/fusion) installation
* Linux
    * [VirtualBox](https://www.virtualbox.org/wiki/Downloads) or [KVM](http://www.linux-kvm.org/) installation
* Windows
    * [Hyper-V](https://github.com/kubernetes/minikube/blob/master/DRIVERS.md#hyperv-driver)
* VT-x/AMD-v virtualization must be enabled in BIOS
* The most recent version of `kubectl`. You can install kubectl following
  [these steps](https://kubernetes.io/docs/user-guide/prereqs/).
* Internet connection
    * You will need a decent internet connection running `minikube start` for the first time for
    Minikube to pull its Docker images. It might take Minikube some time to start.

## Download and Unpack Minikube

See the installation instructions for the
[latest release of minikube](https://github.com/kubernetes/minikube/releases).

## Boot Your First Cluster

We are now ready to boot our first Kubernetes cluster using Minikube!

```
$ minikube start --disk-size=60g --memory=4096
Starting local Kubernetes cluster...
Kubectl is now configured to use the cluster.
```

Now that the cluster is up and ready, `minikube` automatically configures `kubectl` on your machine
with the appropriate authentication and endpoint information.

```
$ kubectl cluster-info
Kubernetes master is running at https://192.168.99.100:8443
KubeDNS is running at https://192.168.99.100:8443/api/v1/proxy/namespaces/kube-system/services/kube-dns
kubernetes-dashboard is running at https://192.168.99.100:8443/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

You are now ready to [install Deis Workflow](install-minikube.md)
