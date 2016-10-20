# Installing Deis Workflow

This document is aimed at those who have already provisioned a [Kubernetes v1.2 or v1.3.4+][] cluster
and want to install Deis Workflow. If help is required getting started with Kubernetes and
Deis Workflow, follow the [quickstart guide](../quickstart/index.md) for assistance.

## Prerequisites

1. Verify the [Kubernetes system requirements](system-requirements.md)
1. Install [Helm Classic and Deis Workflow CLI](../quickstart/install-cli-tools.md) tools

## Check Your Setup

Check that the `helmc` command is available and the version is 0.8 or newer.

```
$ helmc --version
helmc version 0.8.1+a9c55cf
```

Ensure the `kubectl` client is installed and can connect to the Kubernetes cluster. `helmc` uses `kubectl` to interact
with the Kubernetes cluster.

`helmc` can be verified it is working properly by running:

```
$ helmc target
Kubernetes master is running at https://52.9.206.49
Elasticsearch is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/elasticsearch-logging
Heapster is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/heapster
Kibana is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kibana-logging
KubeDNS is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kube-dns
kubernetes-dashboard is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard
Grafana is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/monitoring-grafana
InfluxDB is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/monitoring-influxdb
```

If `helmc target` shows a list of targets like the one above, `helmc` can communicate with the Kubernetes master. Double check that
the master returned by `helmc target` matches the expected cluster.

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

The [Deis Chart Repository](https://github.com/deis/charts) contains everything needed to install Deis Workflow onto
a Kubernetes cluster, with a single `helmc install` command.

Add this repository to Helm Classic:

```
$ helmc repo add deis https://github.com/deis/charts
```

## Install Deis Workflow

Now that Helm Classic is installed and the Deis Chart Repository has been added, install Workflow by running:

```
$ helmc fetch deis/workflow-v2.7.0            # fetches the chart into a
                                              # local workspace
$ helmc generate -x manifests workflow-v2.7.0 # generates various secrets
$ helmc install workflow-v2.7.0               # injects resources into
                                              # your cluster
```

!!! Experimental
	Workflow can also be installed now using the [Kubernetes Helm][helm]. All the details that are needed for a production deployments like off-cluster storage, external registry etc., can be configured by passing an optional [values file][valuesfile] which overrides default values.


    	$ helm repo add deis https://charts.deis.com/workflow  # add the workflow charts repo

    	$ helm install deis/workflow --version=v2.7.0 --namespace=deis -f <optional values file>  # injects resources into your cluster

Helm Classic will install a variety of Kubernetes resources in the `deis` namespace.
Wait for the pods that Helm Classic launched to be ready. Monitor their status by running:

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
NAME                          READY     STATUS    RESTARTS   AGE
deis-builder-hy3xv            1/1       Running   5          5m
deis-controller-g3cu8         1/1       Running   5          5m
deis-database-rad1o           1/1       Running   0          5m
deis-logger-fluentd-1v8uk     1/1       Running   0          5m
deis-logger-fluentd-esm60     1/1       Running   0          5m
deis-logger-sm8b3             1/1       Running   0          5m
deis-minio-4ww3t              1/1       Running   0          5m
deis-registry-asozo           1/1       Running   1          5m
deis-router-k1ond             1/1       Running   0          5m
deis-workflow-manager-68nu6   1/1       Running   0          5m
```

Once all of the pods are in the `READY` state, Deis Workflow is up and running!

After installing Workflow, [register a user and deploy an application](../quickstart/deploy-an-app.md).

[Kubernetes v1.2 or v1.3.4+]: system-requirements.md#kubernetes-versions
[helm]: https://github.com/kubernetes/helm/blob/master/docs/install.md
[valuesfile]: https://charts.deis.com/workflow/values-v2.7.0.yaml
