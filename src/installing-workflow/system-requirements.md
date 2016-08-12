# Requirements

To run Deis Workflow on a Kubernetes cluster, there are a few requirements to keep in mind.

## Kubernetes Versions

Deis Workflow requires Kubernetes v1.2, or v1.3.4 or newer. Workflow is not compatible with
Kubernetes v1.1, and Kubernetes v1.3.0 through v1.3.3 have
[a bug when mounting secrets](https://github.com/deis/workflow/issues/372) which prevents Deis
Workflow from starting.

## Storage Requirements

A variety of Deis Workflow components rely on an object storage system to do their work, including storing application
slugs, Docker images and database logs.

Deis Workflow ships with Minio by default, which provides in-cluster, ephemeral object storage. This means that if the
Minio server crashes, all data will be lost. Therefore, Minio should be used for development or testing only.

Workflow supports Amazon Simple Storage Service (S3), Google Cloud Storage (GCS), OpenShift Swift, and Azure Blob
Storage. See [configuring object storage][storage-configuration] for setup instructions.

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

!!! warning
	Workflow versions prior to 2.2 require '--insecure-registry' to function properly. Depending on
	your Kubernetes and Docker configuration, setting
	`EXTRA_DOCKER_OPTS="--insecure-registry=10.0.0.0/8"` may be sufficient.

## SELinux + OverlayFS

If you are using Docker with OverlayFS, you must disable SELinux by adding `--selinux-enabled=false` to
`EXTRA_DOCKER_OPTS`. For more background information, see:

* [storage-configuration](configuring-object-storage.md)
* [https://github.com/docker/docker/issues/7952](https://github.com/docker/docker/issues/7952)
* [https://github.com/deis/workflow/issues/63](https://github.com/deis/postgres/issues/63)
