# Configuring an Application

A Deis application [stores config in environment variables][].

## Configure the Application

Use `deis config` to modify environment variables for a deployed application.

    $ deis help config
    Valid commands for config:

    config:list        list environment variables for an app
    config:set         set environment variables for an app
    config:unset       unset environment variables for an app
    config:pull        extract environment variables to .env
    config:push        set environment variables from .env

    Use `deis help [command]` to learn more.

When config is changed, a new release is created and deployed automatically.

You can set multiple environment variables with one `deis config:set` command,
or with `deis config:push` and a local .env file.

    $ deis config:set FOO=1 BAR=baz && deis config:pull
    $ cat .env
    FOO=1
    BAR=baz
    $ echo "TIDE=high" >> .env
    $ deis config:push
    Creating config... done, v4

    === yuppie-earthman
    DEIS_APP: yuppie-earthman
    FOO: 1
    BAR: baz
    TIDE: high


## Attach to Backing Services

Deis treats backing services like databases, caches and queues as [attached resources][].
Attachments are performed using environment variables.

For example, use `deis config` to set a `DATABASE_URL` that attaches
the application to an external PostgreSQL database.

    $ deis config:set DATABASE_URL=postgres://user:pass@example.com:5432/db
    === peachy-waxworks
    DATABASE_URL: postgres://user:pass@example.com:5432/db

Detachments can be performed with `deis config:unset`.

## Custom Domains

You can use `deis domains` to add or remove custom domains to your application:

    $ deis domains:add hello.bacongobbler.com
    Adding hello.bacongobbler.com to finest-woodshed... done

Once that's done, you can go into your DNS registrar and set up a CNAME from the new
appname to the old one:

    $ dig hello.deisapp.com
    [...]
    ;; ANSWER SECTION:
    hello.bacongobbler.com.         1759    IN    CNAME    finest-woodshed.deisapp.com.
    finest-woodshed.deisapp.com.    270     IN    A        172.17.8.100

!!! note
    Setting a CNAME for your root domain can cause issues. Setting your @ record
    to be a CNAME causes all traffic to go to the other domain, including mail and the SOA
    ("start-of-authority") records. It is highly recommended that you bind a subdomain to
    an application, however you can work around this by pointing the @ record to the
    address of the load balancer (if any).


## Custom Health Checks

By default, Deis only checks that a container is running. You can add a healthcheck by configuring a
URL, port, initial delay, and timeout value:

    $ deis config:set HEALTHCHECK_URL=/200.html
    === peachy-waxworks
    HEALTHCHECK_URL: /200.html
    $ deis config:set HEALTHCHECK_INITIAL_DELAY=5
    === peachy-waxworks
    HEALTHCHECK_INITIAL_DELAY: 5
    HEALTHCHECK_URL: /200.html
    $ deis config:set HEALTHCHECK_TIMEOUT=5
    === peachy-waxworks
    HEALTHCHECK_TIMEOUT: 5
    HEALTHCHECK_INITIAL_DELAY: 5
    HEALTHCHECK_URL: /200.html
    $ deis config:set HEALTHCHECK_PORT=5000
    === peachy-waxworks
    HEALTHCHECK_TIMEOUT: 5
    HEALTHCHECK_INITIAL_DELAY: 5
    HEALTHCHECK_URL: /200.html
    HEALTHCHECK_PORT: 5000

If a new release does not pass the healthcheck, the application will be rolled back to the previous
release. Beyond that, if an application container responds to a heartbeat check with a different
status than a 200-399, the [router][] will mark that container as down and stop sending
requests to that container.

The health checks are provided by [kubernetes health checks][]. Currently only HTTP GET is supported.

## Track Changes

Each time a build or config change is made to your application, a new [release][] is created.
Track changes to your application using `deis releases`.

    $ deis releases
    === peachy-waxworks Releases
    v4      3 minutes ago                     gabrtv deployed d3ccc05
    v3      1 hour 17 minutes ago             gabrtv added DATABASE_URL
    v2      6 hours 2 minutes ago             gabrtv deployed 7cb3321
    v1      6 hours 2 minutes ago             gabrtv deployed deis/helloworld


## Rollback the Application

Use `deis rollback` to revert to a previous release.

    $ deis rollback v2
    Rolled back to v2

    $ deis releases
    === folksy-offshoot Releases
    v5      Just now                          gabrtv rolled back to v2
    v4      4 minutes ago                     gabrtv deployed d3ccc05
    v3      1 hour 18 minutes ago             gabrtv added DATABASE_URL
    v2      6 hours 2 minutes ago             gabrtv deployed 7cb3321
    v1      6 hours 3 minutes ago             gabrtv deployed deis/helloworld

!!! note
    All releases (including rollbacks) append to the release ledger.


[attached resources]: http://12factor.net/backing-services
[stores config in environment variables]: http://12factor.net/config
[release]: ../reference-guide/terms.md#release
[router]:  ../understanding-deis/components.md#router
[kubernetes health checks]: http://kubernetes.io/v1.1/docs/user-guide/pod-states.html#container-probes
