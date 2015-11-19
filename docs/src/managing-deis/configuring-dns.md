# Configure DNS

For Deis clusters, DNS records must be created. The Deis cluster runs multiple routers infront of the Deis controller and apps you deploy, so a [load balancer][] is recommended.

## Necessary DNS records

Deis requires a wildcard DNS record. Assuming `myapps.com` is the top-level domain
apps will live under:

* `*.myapps.com` should have "A" record entries for each of the load balancer's IP addresses

Apps can then be accessed by browsers at `appname.myapps.com`, and the controller will be available to the Deis client at `deis.myapps.com`.

[AWS recommends][] against creating "A" record entries; instead, create a wildcard "CNAME" record entry for the load balancer's DNS name, or use Amazon [Route 53][].

These records are necessary for all deployments of Deis other than Vagrant clusters.

## Using xip.io

For local Vagrant clusters or for dev clusters, you can use [xip][] to reference the IP of your load balancer. For example:

    $ deis register http://deis.10.21.12.2.xip.io

You would then create the cluster with `10.21.12.2.xip.io` as the cluster domain.

Note that xip does not seem to work for AWS ELBs - you will have to use an actual DNS record.

[AWS recommends]: https://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/using-domain-names-with-elb.html
[load balancer]: configuring-load-balancers.md
[Route 53]: http://aws.amazon.com/route53/
[xip]: http://xip.io/
