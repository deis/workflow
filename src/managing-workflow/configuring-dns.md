# Configure DNS

The Deis Workflow controller and all applications deployed via Workflow are intended (by default) to be accessible as subdomains of the Workflow cluster's domain.  For example, assuming `example.com` were a cluster's domain:

* The controller should be accessible at `deis.example.com`
* Applications should be accessible (by default) at `<application name>.example.com`

Given that this is the case, the primary objective in configuring DNS is that traffic for all subdomains of a cluster's domain be directed to the cluster node(s) hosting the platform's router component, which is capable of directing traffic within the cluster to the correct endpoints.


## With a Load Balancer

Generally, it is recommended that a [load balancer][] be used to direct inbound traffic to one or more routers.  In such a case, configuring DNS is as simple as defining a wildcard record in DNS that points to the load balancer.

For example, assuming a domain of `example.com`:

* An `A` record enumerating each of your load balancer(s) IPs (i.e. DNS round-robining)
* A `CNAME` record referencing an existing fully-qualified domain name for the load balancer
    * Per [AWS' own documentation][AWS recommends], this is the recommended strategy when using AWS Elastic Load Balancers, as ELB IPs may change over time.

DNS for any applications using a "custom domain" (a fully-qualified domain name that is not a subdomain of the cluster's own domain) can be configured by creating a `CNAME` record that references the wildcard record described above.

Although it is dependent upon your distribution of Kubernetes and your underlying infrastructure, in many cases, the IP(s) or existing fully-qualified domain name of a load balancer can be determined directly using the `kubectl` tool:

```
$ kubectl --namespace=deis describe service deis-router | grep "LoadBalancer Ingress"
LoadBalancer Ingress:	a493e4e58ea0511e5bb390686bc85da3-1558404688.us-west-2.elb.amazonaws.com
```

The `LoadBalancer Ingress` field typically describes an existing domain name or public IP(s).  Note that if Kubernetes is able to automatically provision a load balancer for you, it does so asynchronously.  If the command shown above is issued very soon after Workflow installation, the load balancer may not exist yet.

## Without a Load Balancer

On some platforms (Vagrant, for instance), a load balancer is not an easy or practical thing to provision. In these cases, one can directly identify the public IP of a Kubernetes node that is hosting a router pod and use that information to configure the local `/etc/hosts` file.

Because wildcard entries do not work in a local `/etc/hosts` file, using this strategy may result in frequent editing of that file to add fully-qualified subdomains of a cluster for each application added to that cluster.  Because of this a more viable option may be to utilize the [xip.io][xip] service.

In general, for any IP, `a.b.c.d`, the fully-qualified domain name `any-subdomain.a.b.c.d.xip.io` will resolve to the IP `a.b.c.d`.  This can be enormously useful.

To begin, find the node(s) hosting router instances using `kubectl`:

```
$ kubectl --namespace=deis describe pod deis-router | grep Node
Node:       ip-10-0-0-199.us-west-2.compute.internal/10.0.0.199
Node:       ip-10-0-0-198.us-west-2.compute.internal/10.0.0.198
```

The command will display information for every router pod.  For each, a node name and IP are displayed in the `Node` field.  If the IPs appearing in these fields are public, any of these may be used to configure your local `/etc/hosts` file or may be used with [xip.io][xip].  If the IPs shown are not public, further investigation may be needed.

You can list the IP addresses of a node using `kubectl`:

```
$ kubectl describe node ip-10-0-0-199.us-west-2.compute.internal
# ...
Addresses:	10.0.0.199,10.0.0.199,54.218.85.175
# ...
```

Here, the `Addresses` field lists all the node's IPs.  If any of them are public, again, they may be used to configure your local `/etc/hosts` file or may be used with [xip.io][xip].

## Tutorial: Configuring DNS with [Google Cloud DNS][cloud dns]

In this section, we'll describe how to configure Google Cloud DNS for routing your domain name to your Deis cluster.

We'll assume the following in this section:

- Your Deis router service has a load balancer in front of it.
  - The load balancer need not be cloud based, it just needs to provide a stable IP address or a stable domain name
- You have the `mystuff.com` domain name registered with a registrar
  - Replace your domain name with `mystuff.com` in the instructions to follow
- Your registrar lets you alter the nameservers for your domain name (most registrars do)

Here are the steps for configuring cloud DNS to route to your deis cluster:

1. Get the load balancer IP or domain name
  - If you are on Google Container Engine, you can run `kubectl get svc deis-router` and look for the `LoadBalancer Ingress` column to get the IP address
2. Create a new Cloud DNS Zone (on the console: `Networking` => `Cloud DNS`, then click on `Create Zone`)
3. Name your zone, and set the DNS name to `mystuff.com.` (note the `.` at the end
4. Click on the `Create` button
5. Click on the `Add Record Set` button on the resulting page
6. If your load balancer provides a stable IP address, enter the following fields in the resulting form:
  1. `DNS Name`: `*`
  2. `Resource Record Type`: `A`
  3. `TTL`: the DNS TTL of your choosing. If you're testing or you anticipate that you'll tear down and rebuild many deis clusters over time, we recommend a low TTL
  4. `IPv4 Address`: The IP that you got in the very first step
  5. Click the `Create` button
7. If your load balancer provides the stable domain name `lbdomain.com`, enter the following fields in the resulting form:
  1. `DNS Name`: `*`
  2. `Resource Record Type`: `CNAME`
  3. `TTL`: the DNS TTL of your choosing. If you're testing or you anticipate that you'll tear down and rebuild many deis clusters over time, we recommend a low TTL
  4. `Canonical name`: `lbdomain.com.` (note the `.` a the end)
  5. Click on the `Create` button
8. In your domain registrar, set the nameservers for your `mystuff.com` domain to the ones under the `data` column in the `NS` record on the same page. They'll often be something like the below (note the trailing `.` characters).

  ```
  ns-cloud-b1.googledomains.com.
  ns-cloud-b2.googledomains.com.
  ns-cloud-b3.googledomains.com.
  ns-cloud-b4.googledomains.com.
  ```


Note: If you ever have to re-create your deis cluster, simply go back to step 6.4 or 7.4 (depending on your load balancer) and change the IP address or domain name to the new value. You may have to wait for the TTL you set to expire.


## Testing

To test that traffic reaches its intended destination, a request can be
sent to the Deis controller like so (do not forget the trailing slash!):

```
curl http://deis.example.com/v2/
```

Or:

```
curl http://deis.54.218.85.175.xip.io/v2/
```


Since such requests require authentication, a response such as the following should be considered an indicator of success:

```
{"detail":"Authentication credentials were not provided."}
```

[AWS recommends]: https://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/using-domain-names-with-elb.html
[load balancer]: configuring-load-balancers.md
[xip]: http://xip.io/
[cloud dns]: https://cloud.google.com/dns/docs
