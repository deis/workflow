## Find the Load Balancer Address

On Azure Container Engine, Deis Workflow will automatically provision and
attach a Azure Load Balancer to the router component. This component is
responsible for routing HTTP and HTTPS requests from the public internet to
applications that are deployed and managed by Deis Workflow.

Discover the ip address assigned to the `deis-router`, by describing the
`deis-router` service:

```
$ kubectl --namespace=deis get service deis-router
NAME          CLUSTER-IP    EXTERNAL-IP    PORT(S)                            AGE
deis-router   10.0.60.172   13.82.148.57   80/TCP,443/TCP,2222/TCP,9090/TCP   54m
```

If the `EXTERNAL-IP` column shows `<pending>` instead of an ip address continue
to wait until Azure finishes provisioning and attaching the load balancer.

## Prepare the Hostname

Now that an ip address has been attached to the load balancer use the `nip.io`
DNS service to route arbitrary hostnames to the Deis Workflow edge router.
Usage of `nip.io` is not recommended for long-term use and is intended here as
a short cut to prevent fiddling with DNS.

To verify connectivity to the Workflow API server and nip.io, construct the
hostname by taking the ip address of load balancer and adding `nip.io`.

For our example above, the address would be: `13.82.148.57.nip.io`.

Nip answers with the ip address no matter the hostname:
```
$ host 13.82.148.57.nip.io
13.82.148.57.nip.io has address 13.82.148.57
$ host something-random.13.82.148.57.nip.io
something-random.13.82.148.57.nip.io has address 13.82.148.57
```

By default, any HTTP traffic destined for the hostname `deis` is automatically sent to the Workflow API service. To test that everything is connected properly use `curl`:

```
$ curl http://deis.13.82.148.57.nip.io/v2/ && echo
{"detail":"Authentication credentials were not provided."}
```

Since no authentication information has been provided, `curl` will return an error. However this does validate that `curl` has reached the Workflow API service.

Remember the hostname, it will used in the next step.

You are now ready to [register an admin user and deploy your first app](../../deploy-an-app.md).
