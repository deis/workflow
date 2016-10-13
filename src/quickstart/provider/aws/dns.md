## Find Your Load Balancer Hostname

On EC2, Deis Workflow will automatically provision and attach an Elastic Load Balancer (ELB) to the
[Router][]. The Router is responsible for routing HTTP and HTTPS requests from the public internet
to applications that are deployed and managed by Deis Workflow, as well as streaming TCP requests
to the [Builder][].

By describing the `deis-router` service, you can see what hostname allocated by AWS for your Deis
Workflow cluster:

```
$ kubectl --namespace=deis describe svc deis-router | egrep LoadBalancer
Type:                   LoadBalancer
LoadBalancer Ingress:   abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com
```

## Prepare the Hostname

### Using DNS

Now that we have the hostname of the load balancer, let's create the wildcard DNS record that
directs requests from your machine to the application.

First, if you haven't already done so, register your domain name. The Internet Corporation for
Assigned Names and Numbers (ICANN) manages domain names on the Internet. You register a domain name
using a domain name registrar, an ICANN-accredited organization that manages the registry of domain
names. The website for your registrar will provide detailed instructions and pricing information
for registering your domain name. For more information, see the following resources:

 - To use Amazon Route 53 to register a domain name, see [Registering Domain Names Using Amazon Route 53](http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/registrar.html).
 - For a list of accredited registrars, see the [Accredited Registrar Directory](http://www.internic.net/regist.html).

Next, use your DNS service, such as your domain registrar, to create a wildcard CNAME record to
route queries to your load balancer. For more information, see the documentation for your DNS
service.

Alternatively, you can use Amazon Route 53 as your DNS service. You create a hosted zone, which
contains information about how to route traffic on the Internet for your domain, and an alias
resource record set, which routes queries for your domain name to your load balancer.

To create a hosted zone and an alias record set for your domain using Amazon Route 53:

 1. Open the Amazon Route 53 console at https://console.aws.amazon.com/route53/.
 2. Create a Public Hosted Zone with your domain name.
 3. Select the hosted zone that you just created for your domain.
 4. Click Go to Record Sets.
 5. Create a Record Set with the name as `*`, the type as `CNAME - Canonical Name`, and as an alias
    of the Load Balancer created from the router.

### Using nip.io

If you do not have registered a domain name and just want to try out Workflow on AWS, we can use
the `nip.io` wildcard DNS service to route arbitrary hostnames to the Deis Workflow edge router.
This lets us point the Workflow CLI at your cluster without having to either use your own domain or
update DNS!

!!! note
	this is **not** how you should connect to your cluster after the quickstart. This is
	for demonstration purposes only. Instead, you will want to use your own domain name routed to
	the ELB through your domain registrar. AWS actively manages the ELB IPv4 addresses, so what may
	be an IP address associated with your ELB today will be something else later on.

First, pick one of the IP addresses allocated to your ELB:

```
$ host abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com
abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com has address 52.8.166.233
abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com has address 54.193.5.73
```

Grab either address for the next step. We'll use `52.8.166.233` for this example.

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

By default, any HTTP traffic for the hostname `deis` will be sent to the Workflow API service. To
test that everything is connected properly you may validate connectivity using `curl`:

```
$ curl http://deis.52.8.166.233.nip.io/v2/ && echo
{"detail":"Authentication credentials were not provided."}
```

You should see a failed request because we provided no credentials to the API server.

Remember the hostname, we will use it in the next step.

You are now ready to [register an admin user and deploy your first app](../../deploy-an-app.md).

[next: deploy your first app](../../deploy-an-app.md)


[builder]: ../../../understanding-workflow/components.md#builder-builder-slugbuilder-and-dockerbuilder
[router]: ../../../understanding-workflow/components.md#router
