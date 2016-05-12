## Find Your Load Balancer Hostname

On EC2, Deis Workflow will automatically provision and attach a Google Cloud Loadbalancer to the router copmonent. This
component is responsible for routing HTTP and HTTPS requests from the public internet to applications that are deployed
and managed by Deis Workflow.

By describing the `deis-router` service, you can see what hostname allocated by Google Cloud for your Deis Workflow
cluster:

```
$ kubectl describe svc deis-router --namespace=deis | egrep LoadBalancer
Type:                   LoadBalancer
LoadBalancer Ingress:   abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com
```

## Prepare the Hostname

Now that you have the hostname of your load balancer we can use the `nip.io`
DNS service to route arbitrary hostnames to the Deis Workflow edge router. This
lets us point the Workflow CLI at your cluster without having to either use
your own domain or update DNS!

First, pick one of the IP addresses allocated to your ELB:
```
$ host abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com
abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com has address 52.8.166.233
abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com has address 54.193.5.73
```

Note that this is **not** how you should connect to your cluster after the quickstart. Instead you will want to use your
own domain name routed to the ELB CNAME. AWS actively manages the ELB addresses so what may be an ip address associated
with your ELB today will be something else later on.

For now though, grab either address for the next step. We'll use `52.8.166.233` for this example.

To verify the Workflow API server and nip.io, construct your hostname by taking
the ip address for your load balancer and adding `nip.io`. For our example
above, the address would be: `52.8.166.233.nip.io`.

Nip answers with the ip address no matter the hostname:
```
$ host 52.8.166.233.nip.io
52.8.166.233.nip.io has address 52.8.166.233
$ host something-random.52.8.166.233.nip.io
something-random.52.8.166.233.nip.io has address 52.8.166.233
```

By default, any HTTP traffic for the hostname `deis` will be sent to the Workflow API service. To test that everything is connected properly you may validate connectivity using `curl`:

```
$ curl http://deis.52.8.166.233.nip.io/v2/ && echo
{"detail":"Authentication credentials were not provided."}
```

You should see a failed request because we provided no credentials to the API server.

Remember the hostname, we will use it in the next step.

You are now ready to [register an admin user and deploy your first app](../../deploy-an-app.md).

[next: deploy your first app](../../deploy-an-app.md)
