# Installing the Deis Platform

We will use the `helm` utility to provision the Deis platform to a kubernetes cluster. If you don't
have `helm` installed, see [installing helm][helm] for more info.

## Check Your Setup

First check that you have `helm` installed and the version is correct.

    $ helm --version
    0.2.0

Ensure your kubectl client is installed and ensure it can connect to your kubernetes cluster. This
is where `helm` will attempt to communicate with the cluster. You can test that it is working
properly by running

    $ helm target
    Kubernetes master is running at https://10.245.1.2
    Heapster is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/heapster
    KubeDNS is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kube-dns
    KubeUI is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kube-ui
    Grafana is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-grafana
    InfluxDB is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-influxdb

If you see a list of targets like the one above, helm can communicate with the kubernetes master.

## Get the Helm Chart

The [Helm Deis Chart](https://github.com/deis/charts) contains everything you
need to install Deis onto your Kubernetes cluster, with a single `helm install` command.

Run the following commands to set up your Helm environment and install the chart:

```
$ helm update
$ helm repo add deis https://github.com/deis/charts
$ helm fetch deis/deis
```

## Launch Your Deis Cluster

Now that you have it prepared, launch the Deis cluster with:

```
$ helm install deis/deis
```

This command will launch a variety of Kubernetes resources in the `deis` namespace.
You'll need to wait for the pods that it launched to be ready. Monitor their status
by running:

```
$ kubectl get pods --namespace=deis
```

Once you see all of the pods in the `READY` state, your Deis platform is running on a cluster!


[helm]: http://helm.sh
[using deis]: ../using-deis/deploying-an-application.md
[configure dns]: ../managing-deis/configuring-dns.md
