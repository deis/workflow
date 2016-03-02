# Installing Deis Workflow

We will use the Helm package manager for Kubernetes to install Deis Workflow onto a Kubernetes cluster. If you don't have Helm installed, see [Helm's own documentation][helm] for more info.

## Check Your Setup

First check that you have `helm` installed and the version is correct.

```
$ helm --version
0.4.0
```

Ensure your kubectl client is installed and ensure it can connect to your Kubernetes cluster. This
is where Helm will attempt to communicate with the cluster. You can test that it is working
properly by running:

```
$ helm target
Kubernetes master is running at https://10.245.1.2
Heapster is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/heapster
KubeDNS is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kube-dns
KubeUI is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kube-ui
Grafana is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-grafana
InfluxDB is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-influxdb
```

If you see a list of targets like the one above, 'helm' can communicate with the kubernetes master.

## Add the Deis Chart Repository

The [Deis Chart Repository](https://github.com/deis/charts) contains everything you
need to install Deis onto your Kubernetes cluster, with a single `helm install` command.

Run the following command to add this repository to Helm:

```
$ helm repo add deis https://github.com/deis/charts
```

## Install Deis Workflow

Now that you have Helm installed and have added the Deis Chart Repository, install Workflow by running:

```
$ helm fetch deis/deis                 # fetches the chart into a local workspace
$ helm generate -x manifests deis      # generates various secrets
$ helm install deis                    # injects resources into your cluster
```

Helm will install a variety of Kubernetes resources in the `deis` namespace.
You'll need to wait for the pods that it launched to be ready. Monitor their status
by running:

```
$ kubectl get pods --namespace=deis
```

If you would like `kubectl` to automatically update as the pod states change, run (type Ctrl-C to stop the watch):
```
$ kubectl get pods --namespace=deis -w
```

Once you see all of the pods in the `READY` state, Deis Workflow is up and running!

Next, [configure dns][] so you can register your first user.

[helm]: http://helm.sh
[using deis]: ../using-deis/deploying-an-application.md
[configure dns]: ../managing-deis/configuring-dns.md
