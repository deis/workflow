# Configuring Load Balancers

Depending on what distribution of Kubernetes you use and where you host it, installation of Deis Workflow may automatically provision an external (to Kubernetes) load balancer or similar mechanism for directing inbound traffic from beyond the cluster to the Deis router(s).  For example, [kube-aws](https://coreos.com/kubernetes/docs/latest/kubernetes-on-aws.html) and [Google Container Engine](https://cloud.google.com/container-engine/) both do this.  On some other platforms-- Vagrant or bare metal, for instance-- this must either be accomplished manually or does not apply at all.

## Idle connection timeouts

If a load balancer such as the one described above does exist (whether created automatically or manually) and if you intend on handling any long-running requests, the load balancer (or similar) may require some manual configuration to increase the idle connection timeout.  Typically, this is most applicable to AWS and Elastic Load Balancers, but may apply in other cases as well.  It does not apply to Google Container Engine, as the idle connection timeout cannot be configured there, but also works as-is.

If, for instance, Deis Workflow were installed on kube-aws, this timeout should be increased to a recommended value of 1200 seconds.  This will ensure the load balancer does not hang up on the client during long-running operations like an application deployment.  Directions for this can be found [here](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/config-idle-timeout.html).

## Manually configuring a load balancer

If using a Kubernetes distribution or underlying infrastructure that does not support the automated provisioning of a front-facing load balancer, operators will wish to manually configure a load balancer (or use other tricks) to route inbound traffic from beyond the cluster into the cluster to the Deis router(s).  There are many ways to accomplish this.  This documentation will focus on the most common method.  Readers interested in other options may refer to [the router component's own documentation](https://github.com/deis/router#front-facing-load-balancer) for further details.

Begin by determining the "node ports" for the `deis-router` service:


```
$ kubectl --namespace=deis describe service deis-router
```

This will yield output similar to the following:

```
...
Port:			http	80/TCP
NodePort:		http	32477/TCP
Endpoints:		10.2.80.11:80
Port:			https	443/TCP
NodePort:		https	32389/TCP
Endpoints:		10.2.80.11:443
Port:			builder	2222/TCP
NodePort:		builder	30729/TCP
Endpoints:		10.2.80.11:2222
Port:			healthz	9090/TCP
NodePort:		healthz	31061/TCP
Endpoints:		10.2.80.11:9090
...
```

The node ports shown above are high-numbered ports that are allocated on every Kubernetes worker node for use by the router service.  The kube-proxy component on every Kubernetes node will listen on these ports and proxy traffic through to the corresponding port within an endpoint-- that is, a pod running the Deis router.

If manually creating a load balancer, configure it to forward inbound traffic on ports 80, 443, and 2222 (port 9090 can be ignored) to the corresponding node ports on your Kubernetes worker nodes.  Ports 80 and 443 may use either HTTP/S or TCP as protocols.  Port 2222 must use TCP.
