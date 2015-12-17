# Installing the Deis Platform

We will use the `helm` utility to provision the Deis platform to a kubernetes cluster. If you don't
have `helm` installed, see [installing helm][helm] for more info.

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

Once finished, run this command to provision the Deis platform:

    $ helm repo add deis https://github.com/deis/charts
    $ helm install deis/deis

You can then monitor their status by running

```
$ kubectl get pods --namespace=deis
```

Once you see all of the pods ready, your Deis platform is running on a cluster!

## Mapping a Default Domain

Deis will route traffic from Kubernetes nodes to Deis components, but to
do so it needs a domain. By default, Deis is configured to use the
domain `example.com`. For basic Deis testing, simply add an entry to
your host machine's `/etc/hosts` file.

You can find the IP address of a node using `kubectl`:

```
$ kubectl get nodes
NAME         LABELS                              STATUS    AGE
10.245.1.3   kubernetes.io/hostname=10.245.1.3   Ready     19h
```

You may have numerous entries. All entries should be able to route to
Deis, though.

In your `/etc/hosts` file, add an entry like this:

```
10.245.1.3    example.com deis.example.com
```

This route will get you started, though you may find that you have to
manually maintain this file.

### Using a DNS Service

Rather than hard-coding a hostfile entry, you may prefer to [configure a DNS][]
record. `xip.io` is a particularly easy way to do this.

Edit `$(helm home)/workspace/charts/deis/manifests/deis-router-rc.yaml`
and change the `domain` annotation to point to your DNS entry:

```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: deis-router
  namespace: deis
  labels:
    heritage: deis
  annotations:
    deis.io/routerConfig: |
      {
        "domain": "10.245.1.3.xip.io",
        "useProxyProtocol": false
      }
spec:
  replicas: 1
  selector:
    app: deis-router
#...
```

Once you have changed and saved the file, run `kubectl apply`:

```
$ kubectl --namespace=deis apply -f $(helm home)/workspace/charts/deis/manifests/deis-router-rc.yaml
```

After a moment or two, you should be able to test with a brief curl
command:

```
curl http://deis.10.245.1.3.xip.io/v2/
{"detail":"Authentication credentials were not provided."}
```

This message indicates that the message has been routed all the way to
the Deis controller.

Now that you've finished provisioning a cluster, start [Using Deis][] to deploy your first
application on Deis.

[install deisctl]: installing-deisctl.md
[helm]: http://helm.sh
[using deis]: ../using-deis/deploying-an-application.md
[configure dns]: ../managing-deis/configuring-dns.md
