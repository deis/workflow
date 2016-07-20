# Requirements

To run Deis Workflow on a Kubernetes cluster, there are a few requirements to keep in mind.

## Kubernetes Versions

Deis Workflow has been tested with the **Kubernetes v1.2** release line. It is incompatible with Kubernetes v1.1 and earlier. Kubernetes v1.3.0 introduces [a bug when mounting secrets](https://github.com/deis/workflow/issues/372) which prevents Deis Workflow from starting; hopefully this will be fixed in future releases of Kubernetes.

## Resource Requirements

When deploying Deis Workflow, it's important to provision machines with adequate resources. Deis is a highly-available
distributed system, which means that Deis components and your deployed applications will move around the cluster onto
healthy hosts as hosts leave the cluster for various reasons (failures, reboots, autoscalers, etc.). Because of this,
you should have ample spare resources on any machine in your cluster to withstand the additional load of running
services for failed machines.

Deis Workflow components use about 2.5GB of memory across the cluster, and require approximately 30GB of hard disk
space. Because it may need to handle additional load if another one fails, each machine has minimum requirements of:

* At least 4GB of RAM (more is better)
* At least 40GB of hard disk space

Note that these estimates are for Deis Workflow and Kubernetes only. Be sure to leave enough spare capacity for your
application footprint as well.

Running smaller machines will likely result in increased system load and has been known to result in component failures
and instability.

## Docker Insecure Registry

The on-cluster Docker registry is not deployed with TLS enabled. As such, all Kubernetes worker nodes must have their
Docker daemons configured to use an **insecure registry**. The configured subnet should encompass any private networks
used by your worker nodes, including overlay networks.

Depending on your Kubernetes and Docker configuration, setting `EXTRA_DOCKER_OPTS="--insecure-registry=10.0.0.0/8"` may
be sufficient.

## SELinux + OverlayFS

If you are using Docker with OverlayFS, you must disable SELinux by adding `--selinux-enabled=false` to
`EXTRA_DOCKER_OPTS`. For more background information, see:

* [https://github.com/docker/docker/issues/7952](https://github.com/docker/docker/issues/7952)
* [https://github.com/deis/workflow/issues/63](https://github.com/deis/postgres/issues/63)
