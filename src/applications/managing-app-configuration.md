# Configuring an Application

A Deis application [stores config in environment variables][].

## Setting Environment Variables

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


## Custom Health Checks

By default, Workflow only checks that the application starts in their Container. If it is preferred
to have Kubernetes respond to application health, a health check may be added by configuring a
health check probe for the application.

The health checks are implemented as [Kubernetes container probes][kubernetes-probes]. A `liveness`
and a `readiness` probe can be configured, and each probe can be of type `httpGet`, `exec`, or
`tcpSocket` depending on the type of probe the container requires.

A liveness probe is useful for applications running for long periods of time, eventually
transitioning to broken states and cannot recover except by restarting them.

Other times, a readiness probe is useful when the container is only temporarily unable to serve,
and will recover on its own. In this case, if a container fails its readiness probe, the container
will not be shut down, but rather the container will stop receiving incoming requests.

`httpGet` probes are just as it sounds: it performs a HTTP GET operation on the Container. A
response code inside the 200-399 range is considered a pass.

`exec` probes run a command inside the Container to determine its health, such as
`cat /var/run/myapp.pid` or a script that determines when the application is ready. An exit code of
zero is considered a pass, while a non-zero status code is considered a fail.

`tcpSocket` probes attempt to open a socket in the Container. The Container is only considered
healthy if the check can establish a connection. `tcpSocket` probes accept a port number to perform
the socket connection on the Container.

Health checks can be configured on a per-application basis using `deis healthchecks:set`. To
configure a `httpGet` liveness probe:

```
$ deis healthchecks:set liveness httpGet 80
=== peachy-waxworks Healthchecks
Liveness
--------
Initial Delay (seconds): 50
Timeout (seconds): 50
Period (seconds): 10
Success Threshold: 1
Failure Threshold: 3
Exec Probe: N/A
HTTP GET Probe: Path="/" Port=80 HTTPHeaders=[]
TCP Socket Probe: N/A

Readiness
---------
No readiness probe configured.
```

If the application relies on certain headers being set (such as the `Host` header) or a specific
URL path relative to the root, you can also send specific HTTP headers:

```
$ deis healthchecks:set liveness httpGet 80 \
    --path /welcome/index.html \
    --header "X-Client-Version=v1.0"
=== peachy-waxworks Healthchecks
Liveness
--------
Initial Delay (seconds): 50
Timeout (seconds): 50
Period (seconds): 10
Success Threshold: 1
Failure Threshold: 3
Exec Probe: N/A
HTTP GET Probe: Path="/welcome/index.html" Port=80 HTTPHeaders=[X-Client-Version=v1.0]
TCP Socket Probe: N/A

Readiness
---------
No readiness probe configured.
```

To configure an `exec` readiness probe:

```
$ deis healthchecks:set readiness exec -- /bin/echo -n hello
=== peachy-waxworks Healthchecks
Liveness
--------
No liveness probe configured.

Readiness
---------
Initial Delay (seconds): 50
Timeout (seconds): 50
Period (seconds): 10
Success Threshold: 1
Failure Threshold: 3
Exec Probe: Command=[/bin/echo -n hello]
HTTP GET Probe: N/A
TCP Socket Probe: N/A
```

You can overwrite a probe by running `deis healthchecks:set` again:

```
$ deis healthchecks:set readiness httpGet 80
=== peachy-waxworks Healthchecks
Liveness
--------
No liveness probe configured.

Readiness
---------
Initial Delay (seconds): 50
Timeout (seconds): 50
Period (seconds): 10
Success Threshold: 1
Failure Threshold: 3
Exec Probe: N/A
HTTP GET Probe: Path="/" Port=80 HTTPHeaders=[]
TCP Socket Probe: N/A
```

Configured health checks also modify the default application deploy behavior. When starting a new
Pod, Workflow will wait for the health check to pass before moving onto the next Pod.


[attached resources]: http://12factor.net/backing-services
[stores config in environment variables]: http://12factor.net/config
[release]: ../reference-guide/terms.md#release
[router]:  ../understanding-workflow/components.md#router
[kubernetes-probes]: http://kubernetes.io/docs/user-guide/pod-states/#container-probes
