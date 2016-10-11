# Installing Deis Workflow on Vagrant

## Check Your Setup

First check that the `helm` command is available and the version is 0.8 or newer.

```
$ helmc --version
helmc version 0.8.1+a9c55cf
```

Ensure the `kubectl` client is installed and can connect to your Kubernetes cluster. `helm` will
use it to communicate. You can test that it is working properly by running:

```
$ helmc target
Kubernetes master is running at https://10.245.1.2
Heapster is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/heapster
KubeDNS is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kube-dns
kubernetes-dashboard is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard
Grafana is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-grafana
InfluxDB is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-influxdb
```

If you see a list of targets like the one above, `helm` can communicate with the Kubernetes master.

## Add the Deis Chart Repository

The [Deis Chart Repository](https://github.com/deis/charts) contains everything you
need to install Deis onto your Kubernetes cluster, with a single `helmc install` command.

Run the following command to add this repository to Helm:

```
$ helmc repo add deis https://github.com/deis/charts
```

## Install Deis Workflow

Now that you have Helm installed and have added the Deis Chart Repository, install Workflow by running:

```
$ helmc fetch deis/workflow-v2.7.0            # fetches the chart into a
                                              # local workspace
$ helmc generate -x manifests workflow-v2.7.0 # generates various secrets
$ helmc install workflow-v2.7.0               # injects resources into
                                              # your cluster
```

Helm will install a variety of Kubernetes resources in the `deis` namespace.
You'll need to wait for the pods that it launched to be ready. Monitor their status
by running:

```
$ kubectl --namespace=deis get pods
```

If you would like `kubectl` to automatically update as the pod states change, run (type Ctrl-C to stop the watch):
```
$ kubectl --namespace=deis get pods -w
```

Depending on the order in which the Workflow components initialize, some pods may restart. This is common during the
installation: if a component's dependencies are not yet available, that component will exit and Kubernetes will
automatically restart it.

```
$ kubectl --namespace=deis get pods
NAME                          READY     STATUS    RESTARTS   AGE
deis-builder-lrb54            1/1       Running   1          2m
deis-controller-lto6v         1/1       Running   1          2m
deis-database-2jh3w           1/1       Running   0          2m
deis-logger-fluentd-9hm06     1/1       Running   0          2m
deis-logger-yxhwk             1/1       Running   0          2m
deis-minio-p384q              1/1       Running   0          2m
deis-registry-l9l6g           1/1       Running   2          2m
deis-router-yc3rb             1/1       Running   0          2m
deis-workflow-manager-fw5vq   1/1       Running   0          2m
```

Once you see all of the pods in the `READY` state, Deis Workflow is up and running!

Next, [configure dns](dns.md) so you can register your first user and deploy an application.
