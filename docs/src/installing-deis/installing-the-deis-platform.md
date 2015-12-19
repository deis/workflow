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

## Set up the Deis Router

Now that you have the Deis chart, you'll need to make a minor edit to the
`deis-router-rc.yaml` Kubernetes manifest file to prepare the router to accept
incoming traffic on a domain of your choice. Follow the following steps to make
the edit:

1. Open the `$HELM_HOME/workspace/charts/deis/manifests/deis-router-rc.yaml`
file in your favorite editor. Note that if `HELM_HOME` is not in your environment,
it defaults to `~/.helm`
2. Replace `example.com` under `metadata.annotations.deis.io/routerConfig` with
the domain of your choice. This will be called the _platform domain_. You may choose
any domain, but the `Routing Traffic` section below details how to configure DNS or your
host to use that domain properly, so you may want to read that section before proceeding.

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

## A Note on Routing Traffic

As mentioned above, the Deis router component is responsible for accepting traffic
from outside the Kubernetes cluster and directing appropriately. It uses the
incoming request's HTTP `Host` header to direct traffic to Deis components and
to applications deployed via Deis.

### Getting Traffic to the Cluster

You already configured the router with a platform domain in the above setup instructions.
This section details how to configure DNS and/or your local `/etc/hosts` file so that
traffic bound for `*.your-platform.domain` will make it to your Kubernetes cluster
and the Deis router.

#### Using an Automatically Provisioned Load Balancer

If your Kubernetes cluster and the underlying infrastructure
support it, the Deis router's service (which is of `type:
LoadBalancer`) will automatically provision an "external"
(external to the Kubernetes cluster) load balancer.  On AWS,
for instance, this takes the form of an ELB, while on Google
Container Engine, it takes the form of a routing rule.

If it is supported, you will be able to find the DNS name or
IP(s) of the external load balancer like so:

```
$ kubectl describe service deis-router --namespace=deis
```

Examine the `LoadBalancer Ingress` field to find the DNS
name or IP(s).  The former can be added to DNS as a CNAME,
while the latter can be added as an A record.

#### Creating Your Own Load Balancer

On Kubernetes clusters and underlying infrastructure that
do not support the automated provisioning of an external
load balancer for the Deis router, you may provision your
own and add _all_ minion nodes of the Kubernetes cluster to
the pool.

The load balancer must pass incoming traffic on the
following ports to the _same_ ports on the Kubernetes
worker nodes:

* 80
* 443
* 2222
* 9090

The Deis router component listens to those ports on any
host it runs on.  Since not _all_ nodes are likely to
be running the router, a health check should be used to
determine which node(s) can serve requests.  The router's
healthcheck should use the HTTP protocol, port `9090`, and
the request path `/healthz`.

Load balancer idle timeouts should be set to at least `1200`
seconds so connections do not close prematurely during longer
running requests such as application deployments.

#### Without a Load Balancer

On some platforms (Vagrant, for instance) a load balancer is
not an easy or practical thing to provision.  In these cases,
one can directly identify the public IP of a Kubernetes node
that is hosting a router pod and use that information to
configure DNS or the local `/etc/hosts` file.

You can find the IP address of a node using `kubectl`:

```
$ kubectl get pods --namespace=deis | grep deis-router
deis-router-ih25q           1/1       Running   0          2h
```

Using the pod name determined through the above, one can
use `kubectl` to determine what node the pod is running on:

```
$ kubectl describe pod deis-router-ih25q --namespace=deis
```

The `Node` field of the response should provide an IP:

```
Node:				10.245.1.3/
```

If the IP is public, this can be used to configure DNS or the
local `/etc/hosts` file.

In your `/etc/hosts` file, add an entry like this:

```
10.245.1.3    example.com deis.example.com
```

This route will get you started, though you may find that you have to
manually maintain this file.

#### Using a DNS Service

With any of the avenues described above, some hassle may be spared by
leveraging a service such as `xip.io`, which will not require any
editing of DNS records or local `/etc/hosts` files.

Simply determine the correct IP to route your traffic to (as described
above), then configure the router's platform domain to be `<ip>.xip.io`

### Testing

To test that traffic reaches its intended destination, a request can be
sent to the Deis controller like so:

```
curl http://deis.<platform domain>/v2/
```

Since such requests require authentication, a response such as
the following is an indicator of success:

```
{"detail":"Authentication credentials were not provided."}
```

## Next Steps

Now that you've finished provisioning a cluster, start [Using Deis][] to deploy your first
application on Deis.

[install deisctl]: installing-deisctl.md
[helm]: http://helm.sh
[using deis]: ../using-deis/deploying-an-application.md
[configure dns]: ../managing-deis/configuring-dns.md
