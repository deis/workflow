# Installing Deis Workflow

This document is aimed at those who have already provisioned a [Kubernetes v1.3.4+][] cluster
and want to install Deis Workflow. If help is required getting started with Kubernetes and
Deis Workflow, follow the [quickstart guide](../quickstart/index.md) for assistance.

## Prerequisites

1. Verify the [Kubernetes system requirements](system-requirements.md)
1. Install [Helm and Deis Workflow CLI](../quickstart/install-cli-tools.md) tools

## Check Your Setup

Check that the `helm` command is available and the version is v2.1.3 or newer.

```
$ helm version
Client: &version.Version{SemVer:"v2.1.3", GitCommit:"5cbc48fb305ca4bf68c26eb8d2a7eb363227e973", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.1.3", GitCommit:"5cbc48fb305ca4bf68c26eb8d2a7eb363227e973", GitTreeState:"clean"}
```

## Choose Your Deployment Strategy

Deis Workflow includes everything it needs to run out of the box. However, these defaults are aimed at simplicity rather than
production readiness. Production and staging deployments of Workflow should, at a minimum, use off-cluster storage
which is used by Workflow components to store and backup critical data. Should an operator need to completely re-install
Workflow, the required components can recover from off-cluster storage. See the documentation for [configuring object
storage](configuring-object-storage.md) for more details.

More rigorous installations would benefit from using outside sources for the following things:
* [Postgres](configuring-postgres.md) - For example AWS RDS.
* [Registry](configuring-registry.md) - This includes [quay.io](https://quay.io), [dockerhub](https://hub.docker.com), [Amazon ECR](https://aws.amazon.com/ecr/), and [Google GCR](https://cloud.google.com/container-registry/).
* [Redis](../managing-workflow/platform-logging.md#configuring-off-cluster-redis) - Such as AWS Elasticache
* [InfluxDB](../managing-workflow/platform-monitoring.md#configuring-off-cluster-influxdb) and [Grafana](../managing-workflow/platform-monitoring.md#off-cluster-grafana)

## Add the Deis Chart Repository

The Deis Chart Repository contains everything needed to install Deis Workflow onto a Kubernetes cluster, with a single `helm install deis/workflow --namespace deis` command.

Add this repository to Helm:

```
$ helm repo add deis https://charts.deis.com/workflow
```

## Install Deis Workflow

Now that Helm is installed and the repository has been added, install Workflow by running:

```
$ helm install deis/workflow --namespace deis
```

Helm will install a variety of Kubernetes resources in the `deis` namespace.
Wait for the pods that Helm launched to be ready. Monitor their status by running:

```
$ kubectl --namespace=deis get pods
```

If it's preferred to have `kubectl` automatically update as the pod states change, run (type Ctrl-C to stop the watch):

```
$ kubectl --namespace=deis get pods -w
```

Depending on the order in which the Workflow components initialize, some pods may restart. This is common during the
installation: if a component's dependencies are not yet available, that component will exit and Kubernetes will
automatically restart it.

Here, it can be seen that the controller, builder and registry all took a few loops before they were able to start:

```
$ kubectl --namespace=deis get pods
NAME                                     READY     STATUS    RESTARTS   AGE
deis-builder-574483744-l15zj             1/1       Running   0          4m
deis-controller-3953262871-pncgq         1/1       Running   2          4m
deis-database-83844344-47ld6             1/1       Running   0          4m
deis-logger-176328999-wjckx              1/1       Running   4          4m
deis-logger-fluentd-zxnqb                1/1       Running   0          4m
deis-logger-redis-304849759-1f35p        1/1       Running   0          4m
deis-minio-676004970-nxqgt               1/1       Running   0          4m
deis-monitor-grafana-432627134-lnl2h     1/1       Running   0          4m
deis-monitor-influxdb-2729788615-m9b5n   1/1       Running   0          4m
deis-monitor-telegraf-wmcmn              1/1       Running   1          4m
deis-nsqd-3597503299-6mn2x               1/1       Running   0          4m
deis-registry-756475849-lwc6b            1/1       Running   1          4m
deis-registry-proxy-96c4p                1/1       Running   0          4m
deis-router-2126433040-6sl6z             1/1       Running   0          4m
deis-workflow-manager-2528409207-jkz2r   1/1       Running   0          4m
```

Once all of the pods are in the `READY` state, Deis Workflow is up and running!

After installing Workflow, [register a user and deploy an application](../quickstart/deploy-an-app.md).

[Kubernetes v1.3.4+]: system-requirements.md#kubernetes-versions
[helm]: https://github.com/kubernetes/helm/blob/master/docs/install.md
[valuesfile]: https://charts.deis.com/workflow/values-v2.12.0.yaml
