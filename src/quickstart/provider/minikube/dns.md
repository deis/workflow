## Find Your Load Balancer Address

During installation, Deis Workflow specifies that Kubernetes should provision and attach a load
balancer to the router component. The router component is responsible for routing HTTP and HTTPS
requests from outside the cluster to applications that are managed by Deis Worfklow. In cloud
environments, Kubernetes provisions and attaches a load balancer for you. Since we are running in a
local environment, we need to do a little bit of extra work to send requests to the router.

First, determine the ip address allocated to the worker node.

```
$ minikube ip
192.168.99.100
```

## Prepare the Hostname

Now that you have the ip address of your virtual machine, we can use the `nip.io` DNS service or `dnsmasq` to
route arbitrary hostnames to the Deis Workflow edge router. This lets us point the Workflow CLI at
your cluster without having to either use your own domain or update DNS!

### Using `nip.io`

To verify the Workflow API server and nip.io, construct your hostname by taking the ip address for
your load balancer and adding `nip.io`. For our example above, the address would be `192.168.99.100`.

Nip answers with the ip address no matter the hostname:

```
$ host 192.168.99.100.nip.io
192.168.99.100.nip.io has address 192.168.99.100
$ host something-random.192.168.99.100.nip.io
something-random.192.168.99.100.nip.io has address 192.168.99.100
```

### Using DNSMasq

If you `nip.io` is working for you, you can skip this section, and proceed to verify the hostname.

If you prefer not to use `nip.io` or cannot (because your DNS provider might have blocked it), you can use `dnsmasq` on Linux and macOS or `Acrylic` on Windows.

You can install and configure `dnsmasq` on macOS with [Homebrew](https://brew.sh) with the following commands:

```sh
# Installing dnsmasq
$ brew install dnsmasq

# Configure `.minikube` subdomains to always use minikube IP:
$ echo "address=/.minikube/`minikube ip`" >> /usr/local/etc/dnsmasq.conf
$ sudo brew services start dnsmasq

# Make the system resolver use dnsmasq to resolve addresses:
$ sudo mkdir /etc/resolver
$ echo nameserver 127.0.0.1 | sudo tee /etc/resolver/minikube

# You might need to clear the DNS resolver cache:
$ sudo killall -HUP mDNSResponder
```

To verify the hostname, you will need to use `deis.minikube` as hostname instead of `deis.192.168.99.100.nip.io` in the next section. We will also use it in the next step.

### Verify the hostname

By default, any HTTP traffic for the hostname `deis` will be sent to the Workflow API service. To test that everything is connected properly you may validate connectivity using `curl`:

```
$ curl http://deis.192.168.99.100.nip.io/v2/ && echo
{"detail":"Authentication credentials were not provided."}
```

You should see a failed request because we provided no credentials to the API server.

Remember the hostname, we will use it in the next step.

[next: deploy your first app](../../deploy-an-app.md)
