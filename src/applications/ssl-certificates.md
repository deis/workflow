# Application SSL Certificates

SSL is a cryptographic protocol that provides end-to-end encryption and integrity for all web
requests. Apps that transmit sensitive data should enable SSL to ensure all information is
transmitted securely.

To enable SSL on a custom domain, e.g., `www.example.com`, use the SSL endpoint.

!!! note
    `deis certs` is only useful for custom domains. Default application domains are
    SSL-enabled already and can be accessed simply by using https,
    e.g. `https://foo.deisapp.com` (provided that you have [installed your wildcard
    certificate][platform-ssl] on the routers or on the load balancer).


## Overview

Because of the unique nature of SSL validation, provisioning SSL for your domain is a multi-step
process that involves several third-parties. You will need to:

1. Purchase an SSL certificate from your SSL provider
2. Upload the cert to Deis


## Acquire SSL Certificate

Purchasing an SSL cert varies in cost and process depending on the vendor. [RapidSSL][] offers a
simple way to purchase a certificate and is a recommended solution. If you’re able to use this
provider, see [buy an SSL certificate with RapidSSL][] for instructions.


## DNS and Domain Configuration

Once the SSL certificate is provisioned and your cert is confirmed, you must route requests for
your domain through Deis. Unless you've already done so, add the domain specified when generating
the CSR to your app with:

    $ deis domains:add www.example.com -a foo
    Adding www.example.com to foo... done


## Add a Certificate

Add your certificate, any intermediate certificates, and private key to the endpoint with the
`certs:add` command.

    $ deis certs:add example-com server.crt server.key
    Adding SSL endpoint... done
    www.example.com

!!! note
    The name given to the certificate can only contain a-z (lowercase), 0-9 and hyphens

The Deis platform will investigate the certificate and extract any relevant information from it
such as the Common Name, Subject Alt Names (SAN), fingerprint and more.

This allows for wildcard certificates and multiple domains in the SAN without uploading duplicates.

### Add a Certificate Chain

Sometimes, your certificates (such as a self-signed or a cheap certificate) need additional
certificates to establish the chain of trust. What you need to do is bundle all the certificates
into one file and give that to Deis. Importantly, your site’s certificate must be the first one:

    $ cat server.crt server.ca > server.bundle

After that, you can add them to Deis with the `certs:add` command:

    $ deis certs:add example-com server.bundle server.key
    Adding SSL endpoint... done
    www.example.com

## Attach SSL certificate to a domain

Certificates are not automagically connected up to domains, instead you will have to attach a
certificate to a domain

    $ deis certs:attach example-com example.com

Each certificate can be connected to many domains. There is no need to upload duplicates.

To remove an association

    $ deis certs:detach example-com example.com

## Endpoint overview

You can verify the details of your domain's SSL configuration with `deis certs`.

    $ deis certs

         Name     |    Common Name    | SubjectAltName    |         Expires         |   Fingerprint   |   Domains    |   Updated   |   Created
    +-------------+-------------------+-------------------+-------------------------+-----------------+--------------+-------------+-------------+
      example-com |     example.com   | blog.example.com  | 31 Dec 2017 (in 1 year) | 8F:8E[...]CD:EB |  example.com | 30 Jan 2016 | 29 Jan 2016


or by looking at at each certificates detailed information

    $ deis cert:info example-com

    === bar-com Certificate
    Common Name(s):     example.com
    Expires At:         2017-01-14 23:57:57 +0000 UTC
    Starts At:          2016-01-15 23:57:57 +0000 UTC
    Fingerprint:        7A:CA:B8:50:FF:8D:EB:03:3D:AC:AD:13:4F:EE:03:D5:5D:EB:5E:37:51:8C:E0:98:F8:1B:36:2B:20:83:0D:C0
    Subject Alt Name:   blog.example.com
    Issuer:             /C=US/ST=CA/L=San Francisco/O=Deis/OU=Engineering/CN=example.com/emailAddress=engineering@deis.com
    Subject:            /C=US/ST=CA/L=San Francisco/O=Deis/OU=Engineering/CN=example.com/emailAddress=engineering@deis.com

    Connected Domains:  example.com
    Owner:              admin-user
    Created:            2016-01-28 19:07:41 +0000 UTC
    Updated:            2016-01-30 00:10:02 +0000 UTC

## Testing SSL

Use a command line utility like `curl` to test that everything is configured correctly for your
secure domain.

!!! note
    The -k option flag tells curl to ignore untrusted certificates.

Pay attention to the output. It should print `SSL certificate verify ok`. If it prints something
like `common name: www.example.com (does not match 'www.somedomain.com')` then something is not
configured correctly.

## Enforcing SSL at the Router

To enforce all HTTP requests be redirected to HTTPS, TLS can be enforced at the router level by
running

    $ deis tls:enable -a foo
    Enabling https-only requests for foo... done

Users hitting the HTTP endpoint for the application will now receive a 301 redirect to the HTTPS
endpoint.

To disable enforced TLS, run

    $ deis tls:disable -a foo
    Disabling https-only requests for foo... done

## Remove Certificate

You can remove a certificate using the `certs:remove` command:

    $ deis certs:remove my-cert
    Removing www.example.com... Done.

## Swapping out certificates

Over the lifetime of an application an operator will have to acquire certificates with new expire
dates and apply it to all relevant applications, below is the recommended way to swap out certificates.

Be intentional with certificate names, name them `example-com-2017` when possible, where the year
signifies the expiry year. This allows for `example-com-2018` when a new certificate is purchased.

Assuming all applications are already using `example-com-2017` the following commands can be ran,
chained together or otherwise:

    $ deis certs:detach example-com-2017 example.com
    $ deis certs:attach example-com-2018 example.com

This will take care of a singular domain which allows the operator to verify everything went
as planned and slowly roll it out to any other application using the same method.

## Troubleshooting

Here are some steps you can follow if your SSL endpoint is not working as you'd expect.


### Untrusted Certificate

In some cases when accessing the SSL endpoint, it may list your certificate as untrusted.

If this occurs, it may be because it is not trusted by Mozilla’s list of [root CAs][]. If this is
the case, your certificate may be considered untrusted for many browsers.

If you have uploaded a certificate that was signed by a root authority but you get the message that
it is not trusted, then something is wrong with the certificate. For example, it may be missing
[intermediary certificates][]. If so, download the intermediary certificates from your SSL provider,
remove the certificate from Deis and re-run the `certs:add` command.

[RapidSSL]: https://www.rapidssl.com/
[buy an SSL certificate with RapidSSL]: https://www.rapidssl.com/buy-ssl/
[platform-ssl]: ../managing-workflow/platform-ssl.md
[root CAs]: https://www.mozilla.org/en-US/about/governance/policies/security-group/certs/included/
[intermediary certificates]: http://en.wikipedia.org/wiki/Intermediate_certificate_authorities
