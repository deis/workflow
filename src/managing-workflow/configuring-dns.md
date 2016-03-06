# Configure DNS

For Deis clusters, DNS records must be created. The Deis cluster runs multiple routers infront of the Deis controller and apps you deploy, so a [load balancer][] is recommended.

You can find the IP addresses of your Kubernetes cluster nodes by
running `kubectl get nodes`.

## Necessary DNS records

Deis requires a wildcard DNS record. Assuming `myapps.com` is the top-level domain
apps will live under:

* `*.myapps.com` should have "A" record entries for each of the load balancer's IP addresses

Apps can then be accessed by browsers at `appname.myapps.com`, and the controller will be available to the Deis client at `deis.myapps.com`.

[AWS recommends][] against creating "A" record entries; instead, create a wildcard "CNAME" record entry for the load balancer's DNS name, or use Amazon [Route 53][].

These records are necessary for all deployments of Deis other than Vagrant clusters.

## DNS without a Load Balancer

On some platforms (Vagrant, for instance), a load balancer is not an easy or practical thing to
provision. In these cases, one can directly identify the public IP of a Kubernetes node that is
hosting a router pod and use that information to configure DNS or the local `/etc/hosts` file.

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

An easy way to configure wildcard DNS is to use [xip.io][] to reference the IP of the node running
your router. For example:

    $ deis register http://deis.10.245.1.3.xip.io

Note that xip does not seem to work for AWS ELBs - you will have to use an actual DNS record.

Alternatively, in your `/etc/hosts` file, add an entry like this:

```
10.245.1.3    example.com deis.example.com
```

This will get you started, though you may find that you have to manually maintain this file as you
create and deploy more applications to the cluster.

## Testing

To test that traffic reaches its intended destination, a request can be
sent to the Deis controller like so (do not forget the trailing slash!):

```
curl http://deis.example.com/v2/
```

Since such requests require authentication, a response such as
the following is an indicator of success:

```
{"detail":"Authentication credentials were not provided."}
```

[AWS recommends]: https://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/using-domain-names-with-elb.html
[load balancer]: configuring-load-balancers.md
[Route 53]: http://aws.amazon.com/route53/
[xip]: http://xip.io/
