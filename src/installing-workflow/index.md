# Installing Deis Workflow

This document is aimed at those who have already provisioned a Kubernetes cluster and want to install Deis Workflow. If
you are just getting started with Kubernetes and Deis Workflow, follow our [quickstart guide](../quickstart/index.md)
with help booting Kubernetes and installing Workflow.


## Prerequisites

You need to [install Helm Classic and Deis Workflow CLI before continuing](../quickstart/install-cli-tools.md).

## Check Your Setup

Check that the `helmc` command is available and the version is 0.7 or newer.

```
$ helmc --version
helmc version 0.7.0+20a7ed7
```

Ensure the `kubectl` client is installed and can connect to your Kubernetes cluster. `helmc` uses `kubectl` to interact
with your Kubernetes cluster.

You can test that `helmc` and `kubectl` are working properly by running:

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

If you see a list of targets like the one above, `helmc` can communicate with the Kubernetes master. Double check that
the master returned by `helmc target` matches the expected cluster.

## Add the Deis Chart Repository

The [Deis Chart Repository](https://github.com/deis/charts) contains everything you need to install Deis Workflow onto
your Kubernetes cluster, with a single `helmc install` command.

Add this repository to Helm Classic:

```
$ helmc repo add deis https://github.com/deis/charts
```

## Install Deis Workflow

Now that you have Helm Classic installed and have added the Deis Chart Repository, install Workflow by running:

```
$ helmc fetch deis/workflow-beta4             # fetches the chart into a
                                              # local workspace
$ helmc generate -x manifests workflow-beta4  # generates various secrets
$ helmc install workflow-beta4                # injects resources into
                                              # your cluster
```

Helm Classic will install a variety of Kubernetes resources in the `deis` namespace.
You'll need to wait for the pods that it launched to be ready. Monitor their status
by running:

```
$ kubectl get pods --namespace=deis
```

If you would like `kubectl` to automatically update as the pod states change, run (type Ctrl-C to stop the watch):
```
$ kubectl get pods --namespace=deis -w
```

Depending on the order in which the Workflow components start, you may see a few components restart. This is common during the installation process, if a component's dependencies are not yet available the component will exit and Kubernetes will automatically restart the containers.

Here, you can see that controller, builder and registry all took a few loops before there were able to start:
```
$ kubectl get pods --namespace=deis
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

Once you see all of the pods in the `READY` state, Deis Workflow is up and running!
