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

    $ helm update
    $ helm repo add deis https://github.com/deis/charts
    $ helm install deis/deis

You can then monitor their status by running

```
$ kubectl get pods --namespace=deis
```

Once you see all of the pods ready, your Deis platform is running on a cluster!

## Routing Traffic

The Deis router component will use an incoming request's HTTP `Host`
header to direct traffic to Deis components and to applications deployed
via Deis. It is therefore important that the router be configured
properly and that DNS and/or your local `/etc/hosts` file are as well.

### Configuring the Platform Domain

The Deis router requires a "platform domain" be set.  Deis components
that respond to HTTP requests and applications deployed via Deis will
all live on subdomains of the platform domain.  When installing Deis
via helm, the platform domain is set to `example.com` by default.  This
can be changed by editing Deis' helm chart prior to installation.
Alternatively, the change can be made after Deis has been installed
by editing the router's replication controller like so:

```
$ kubectl edit rc deis-router --namespace=deis
```

Find `example.com` in the manifest, change it to a domain of your
choosing, and save changes.  Kubernetes will apply the changes and
the router will dynamically reconfigure itself accordingly.

### Getting Traffic to the Cluster

With the platform domain configured, the only remaining concern
is to ensure traffic for that domain reaches the cluster.  There
are a few ways of doing this, and which you use may depend on the
capabilities of your infrastructure and your Kubernetes cluster.

In general, the goal is to connect traffic bound for
`*.the-domain-you.picked` to your Kubernetes cluster.

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
