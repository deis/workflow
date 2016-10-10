# Platform SSL

SSL/TLS is the standard security technology for establishing an encrypted link between a web server
and a browser. This link ensures that all data passed between the web server and browsers remain
private and integral.

To enable SSL for the Workflow API and all managed apps, you can add an SSL certificate to the Deis Workflow router. You
must provide either an SSL certificate that was registered with a CA or [your own self-signed SSL
certificate](../reference-guide/creating-a-self-signed-ssl-certificate.md).

Note that the platform SSL certificate also functions as a default certificate for your apps that are deployed via
Workflow. If you would like to attach a specific certificate to an application and domain see [Application SSL
Certificates](../applications/ssl-certificates.md).

## Installing SSL on the Deis Router

To terminate SSL connections on the Deis Router use `kubectl` to create a new Secret at a known name. The Deis Workflow
router will automatically detect this secret and reconfigure itself appropriately.

The following criteria must be met:

 - The name of the secret must be `deis-router-platform-cert`
 - The certificate's public key must be supplied as the value of the `cert` key
 - The certificate's private key must be supplied as the value of the `key` key
 - Both the certificate and private key must be base64 encoded

If your certificate has intermediate certs, append the intermediate signing certs to the bottom of the `cert` file
before base64 encoding the combined certificates.

Prepare your certificate and key files by encoding them in base64:

```
$ cat certificate-file.crt
-----BEGIN CERTIFICATE-----
/ * your SSL certificate here */
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
/* any intermediate certificates */
-----END CERTIFICATE-----
$ cat certificate-file.crt | base64 -e
LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCi8gKiB5b3VyIFNTTCBjZXJ0aWZpY2F0ZSBoZXJlICovCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0KLS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCi8qIGFueSBpbnRlcm1lZGlhdGUgY2VydGlmaWNhdGVzICovCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
$ cat certificate.key
-----BEGIN RSA PRIVATE KEY-----
/* your unencrypted private key here */
-----END RSA PRIVATE KEY-----
$ cat certificate.key | base64 -e
LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQovKiB5b3VyIHVuZW5jcnlwdGVkIHByaXZhdGUga2V5IGhlcmUgKi8KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0K
```

Open your favorite text editor and create the Kubernetes manifest:

```
$ $EDITOR deis-router-platform-cert.yaml
```

The format of the Secret manifest should match the below example. Make sure you paste the appropriate values for `cert`
and `key` from the above examples:

```
$ cat deis-router-platform-cert.yaml
apiVersion: v1
kind: Secret
metadata:
  name: deis-router-platform-cert
  namespace: deis
type: Opaque
data:
  tls.crt: LS0...tCg==
  tls.key: LS0...LQo=
```

Once you've created the `deis-router-platform-cert.yaml` file, you can install the manifest with `kubectl create -f
deis-router-platform-cert.yaml`. The Deis Workflow router will automatically notice the new secret and update its 
configuration on-the-fly.

## Installing SSL on a Load Balancer

Most cloud-based load balancers also support SSL termination in addition to passing traffic through to Deis Router.  Any
communication inbound to the load balancer will be encrypted while the internal components of Deis Workflow will still
communicate over HTTP. This offloads SSL processing to the cloud load balancer but also means that any
application-specific SSL certificates must **also** be configured on the cloud load balancer.

To terminate SSL on the cloud load balancer you will need to modify the load balancer's listener settings:

 - Swap the load balancer protocol on port 443 to use HTTPS instead of TCP
 - Swap the backend protocol to use HTTP instead of TCP
 - Change the destination backend port to match the port configured for HTTP, usually port 80
 - Install the certificate on the listener associated with port 443

See your vendor's specific instructions on installing SSL on your load balancer. For AWS, see their
documentation on [installing an SSL cert for load balancing](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/ssl-server-cert.html).
