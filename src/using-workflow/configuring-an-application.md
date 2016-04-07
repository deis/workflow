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

By default, Workflow only checks that your application containers start in
their Pod. If you would like Kubernetes to respond to appliation health, you
may add a health check by configuring URL, port, initial delay, and timeout
values.

The health checks are implemented as [Kubernetes container probes][kubernetes-probes]. Currently only HTTP GET is supported.

Available configuration options for health checks are the following, including defaults:

**HEALTHCHECK_URL**

Path in the application to use for health check, such as /healthz - This value needs to be set for any health check to happen. Needs to accept a HTTP GET request and return a HTTP status between 200-399.

**HEALTHCHCK_PORT**

TCP port to use for health check. Defaults to using same port as the application

**HEALTHCHECK_TIMEOUT**

Number of seconds after which the health check times out. Defaults to 50 seconds

**HEALTHCHECK\_INITIAL_DELAY**

Number of seconds before health checks starts checking the application after the start of the pod.

This is useful to set if the application takes a while to get setup, due to migrations, cache warming or otherwise. Prevents Kubernetes (and Deis Workflow) from replacing an application pod in its setup phase.

Defaults to 50 seconds

**HEALTHCHECK\_PERIOD_SECONDS**

How often (in seconds) to perform the health check. Defaults every 10 seconds

**HEALTHCHECK\_SUCCESS_THRESHOLD**

Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1 success

**HEALTHCHECK\_FAILURE_THRESHOLD**

Minimum consecutive failures for the probe to be considered failed after having succeeded. Defaults to 3 failures


Configure these health checks on a per-application basis using `deis config:set`:
```
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
```

If an application times out, or responds to a health check with a response code
outside the 200-399 range, Kubernetes will stop sending requests to the
application and re-schedule the pod to another node.

Configured health checks also modify the default application deploy behavior.
When starting a new pod, Workflow will wait for the health check to pass before
moving onto the next pod.

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
[router]:  ../understanding-workflow/components.md#router
[kubernetes-probes]: http://kubernetes.io/docs/user-guide/pod-states/#container-probes
