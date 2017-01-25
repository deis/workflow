# Installing Deis Workflow on Amazon Web Services

{!install-workflow.md!}

## Configure your AWS Load Balancer

After installing Workflow on your cluster, you will need to adjust your load balancer
configuration. By default, the connection timeout for Elastic Load Blancers is 60 seconds.
Unfortunately, this timeout is too short for long running connections when using `git push`
functionality of Deis Workflow.

Deis Workflow will automatically provision and attach a Elastic Loadbalancer to the router
component. This component is responsible for routing HTTP and HTTPS requests from the public
internet to applications that are deployed and managed by Deis Workflow.

By describing the `deis-router` service, you can see what IP hostname has been allocated by AWS for
your Deis Workflow cluster:

```
$ kubectl --namespace=deis describe svc deis-router | egrep LoadBalancer
Type:                   LoadBalancer
LoadBalancer Ingress:   abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com
```

The AWS name for the ELB is the first part of hostname, before the `-`. List all of your ELBs by
name to confirm:

```
$ aws elb describe-load-balancers --query 'LoadBalancerDescriptions[*].LoadBalancerName'
abce0d48217d311e69a470643b4d9062
```

Set the connection timeout to 1200 seconds, make sure you use your load balancer name:

```
$ aws elb modify-load-balancer-attributes \
        --load-balancer-name abce0d48217d311e69a470643b4d9062 \
        --load-balancer-attributes "{\"ConnectionSettings\":{\"IdleTimeout\":1200}}"
abce0d48217d311e69a470643b4d9062
CONNECTIONSETTINGS	1200
```
