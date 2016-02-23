# Creating a Self-Signed SSL Certificate

When [using the app ssl][app ssl] feature for non-production applications or when [installing SSL for the platform][platform ssl], you can avoid the costs associated with the SSL certificate by using a self-signed SSL certificate. Though the certificate implements full encryption, visitors to your site will see a browser warning indicating that the certificate should not be trusted.

## Prerequisites

The openssl library is required to generate your own certificate. Run the following command in your local environment to see if you already have openssl installed.

    $ which openssl
    /usr/bin/openssl

If the which command does not return a path then you will need to install openssl yourself:

If you have... | Install with...
---------------|------------------------
Mac OS X       | Homebrew: `brew install openssl`
Windows        | complete package .exe installed
Ubuntu Linux   | `apt-get install openssl`

## Generate Private Key and Certificate Signing Request

A private key and certificate signing request are required to create an SSL certificate. These can be generated with a few simple commands. When the openssl req command asks for a “challenge password”, just press return, leaving the password empty.

    $ openssl genrsa -des3 -passout pass:x -out server.pass.key 2048
    ...
    $ openssl rsa -passin pass:x -in server.pass.key -out server.key
    writing RSA key
    $ rm server.pass.key
    $ openssl req -new -key server.key -out server.csr
    ...
    Country Name (2 letter code) [AU]:US
    State or Province Name (full name) [Some-State]:California
    ...
    A challenge password []:
    ...

## Generate SSL Certificate

The self-signed SSL certificate is generated from the server.key private key and server.csr files.

    $ openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

The server.crt file is your site certificate suitable for use with [Deis's SSL endpoint][app ssl] along with the server.key private key.

[app ssl]: ../using-deis/application-ssl-certificates.md
[platform ssl]: ../managing-deis/platform-ssl.md
