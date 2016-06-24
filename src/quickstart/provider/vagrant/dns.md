## Find Your Load Balancer Address

During installation, Deis Workflow specifies that Kubernetes should provision and attach a load balancer to the router
component. The router component is responsible for routing HTTP and HTTPS requests from outside the cluster to
applications that are managed by Deis Worfklow. In cloud environments Kubernetes provisions and attaches a load balancer
for you. Since we are running in a local environment, we need to do a little bit of extra work to manage routes into the
Kubernetes overlay network.

First, determine the ip address allocated to your worker node.

```
$ kubectl get nodes
NAME                STATUS    AGE
kubernetes-node-1   Ready     4h
$ kubectl describe node kubernetes-node-1 | egrep Addresses
Addresses:      10.245.1.3,10.245.1.3
```

Here, our node address is `10.254.1.3`.

Next, determine the ip address of the Deis Workflow router component:

```
$ kubectl --namespace=deis describe service deis-router | egrep IP
IP:                     10.247.114.249
```

The service address for the router is `10.247.114.249`.

Last, we need to inform your machine how to reach the service address.

Add routes on Linux with:
```
$ sudo route add 10.247.114.249 gw 10.245.1.3
```

Add routes on Mac OS X with:
```
$ sudo route add 10.247.114.249 10.245.1.3
Password:
add host 10.247.114.249: gateway 10.245.1.3
```

This tells your machine that the service address `10.247.114.249` can be reached by forwarding the packets to the worker
node found at `10.245.1.3`.

**Remember when you are finished experimenting, you should remove the route so you aren't confused later:**

Remove routes on Linux with:
```
$ sudo route del 10.247.114.249
```

Remove routes on Mac OS X with:

```
$ sudo route delete 10.247.114.249 10.245.1.3
delete host 10.247.114.249: gateway 10.245.1.3
```

## Prepare the Hostname

Now that you have the ip address of your service and routing configured we can use the `nip.io` DNS service to route
arbitrary hostnames to the Deis Workflow edge router. This lets us point the Workflow CLI at your cluster without having
to either use your own domain or update DNS!

To verify the Workflow API server and nip.io, construct your hostname by taking the ip address for your load balancer
and adding `nip.io`. For our example above, the address would be: `10.247.114.249`.

Nip answers with the ip address no matter the hostname:
```
$ host 10.247.114.249.nip.io
10.247.114.249.nip.io has address 10.247.114.249
$ host something-random.10.247.114.249.nip.io
something-random.10.247.114.249.nip.io has address 10.247.114.249
```

By default, any HTTP traffic for the hostname `deis` will be sent to the Workflow API service. To test that everything is connected properly you may validate connectivity using `curl`:

```
$ curl http://deis.10.247.114.249.nip.io/v2/ && echo
{"detail":"Authentication credentials were not provided."}
```

You should see a failed request because we provided no credentials to the API server.

Remember the hostname, we will use it in the next step.

[next: deploy your first app](../../deploy-an-app.md)
