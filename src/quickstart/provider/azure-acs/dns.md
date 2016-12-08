## Find Your Load Balancer Address

On Azure Container Engine, Deis Workflow will automatically provision and
attach a Azure Load Balancer to the router component. This component is
responsible for routing HTTP and HTTPS requests from the public internet to
applications that are deployed and managed by Deis Workflow.

By describing the `deis-router` service, you can see what IP address has been
allocated by Azure Cloud for your Deis Workflow cluster:

```
$ kubectl --namespace=deis get service deis-router
NAME          CLUSTER-IP    EXTERNAL-IP    PORT(S)                            AGE
deis-router   10.0.60.172   13.82.148.57   80/TCP,443/TCP,2222/TCP,9090/TCP   54m
```

TODO: mention `<pending>` state

## Prepare the Hostname

Now that you have the ip address of your load balancer we can use the `nip.io`
DNS service to route arbitrary hostnames to the Deis Workflow edge router. This
lets us point the Workflow CLI at your cluster without having to either use
your own domain or update DNS!

To verify the Workflow API server and nip.io, construct your hostname by taking
the ip address for your load balancer and adding `nip.io`. For our example
above, the address would be: `13.82.148.57.nip.io`.

Nip answers with the ip address no matter the hostname:
```
$ host 13.82.148.57.nip.io
13.82.148.57.nip.io has address 13.82.148.57
$ host something-random.13.82.148.57.nip.io
something-random.13.82.148.57.nip.io has address 13.82.148.57
```

By default, any HTTP traffic for the hostname `deis` will be sent to the Workflow API service. To test that everything is connected properly you may validate connectivity using `curl`:

```
$ curl http://deis.13.82.148.57.nip.io/v2/ && echo
{"detail":"Authentication credentials were not provided."}
```

You should see a failed request because we provided no credentials to the API server.

Remember the hostname, we will use it in the next step.

You are now ready to [register an admin user and deploy your first app](../../deploy-an-app.md).
