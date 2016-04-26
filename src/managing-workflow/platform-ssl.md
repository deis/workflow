# Platform SSL

SSL/TLS is the standard security technology for establishing an encrypted link between a web server
and a browser. This link ensures that all data passed between the web server and browsers remain
private and integral.

To enable SSL for your cluster and all apps running upon it, you can add an SSL key to your load
balancer. You must either provide an SSL certificate that was registered with a CA or provide
[your own self-signed SSL certificate](../reference-guide/creating-a-self-signed-ssl-certificate.md).

## Installing SSL on a Load Balancer

On most cloud-based load balancers, you can install a SSL certificate onto the load balancer
itself. Any communication inbound to the load balancer will be encrypted while the internal
components of Deis will still communicate over HTTP.

When you install Deis, Kubernetes will provision a load balancer for the routers. To enable SSL,
you will need to modify the listener settings on the load balancer:

 - swap the load balancer protocol on port 443 to use HTTPS
 - swap the backend protocol to use HTTP
 - change the backend port to the same backend port as the listener on port 80
 - install the certificate on the listener for port 443

See your vendor's specific instructions on installing SSL on your load balancer. For AWS, see their
documentation on [installing an SSL cert for load balancing](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/ssl-server-cert.html).

## Installing SSL on the Deis Routers

You can also use the Deis routers to terminate SSL connections. Use `kubectl` to install the
certificate and private keys. Open your favorite text editor and create the Kubernetes manifest:

	$ $EDITOR deis-router-platform-cert.yaml

At this point, you'll want to create a new Kubernetes secret bearing the wildcard certificate.
The following criteria must be met:

 - The name must be deis-router-platform-cert
 - The certificate's public key must be supplied as the value of the `cert` key
 - The certificate's private key must be supplied as the value of the `key` key
 - Both the certificate and private key must be base64 encoded

For example:

	$ cat deis-router-platform-cert.yaml
	apiVersion: v1
	kind: Secret
	metadata:
	  name: deis-router-platform-cert
	  namespace: deis
	type: Opaque
	data:
	  cert: LS0...tCg==
	  key: LS0...LQo=

If your certificate has intermediate certs that need to be presented as part of a certificate
chain, append the intermediate certs to the bottom of the `cert` value before base64 encoding the
cert chain.

Once you've created the certificate manifest, you can then install the certificate with
`kubectl create -f deis-router-platform-cert.yaml`. The router will pick this up and update its
configuration on-the-fly.
