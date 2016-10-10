# Managing an Application

## Track Application Changes

Deis Workflow tracks all changes to your application. Application changes are the result of either new application code
pushed to the platform (via `git push deis master`), or an update to application configuration (via `deis config:set KEY=VAL`).

Each time a build or config change is made to your application a new [release][] is created. These release numbers
increase monotonically.

You can see a record of changes to your application using `deis releases`:

```
$ deis releases
=== peachy-waxworks Releases
v4      3 minutes ago                     gabrtv deployed d3ccc05
v3      1 hour 17 minutes ago             gabrtv added DATABASE_URL
v2      6 hours 2 minutes ago             gabrtv deployed 7cb3321
v1      6 hours 2 minutes ago             gabrtv deployed deis/helloworld
```

## Rollback a Release

Deis Workflow also supports rolling back go previous releases. If buggy code or an errant configuration change is pushed
to your application, you may rollback to a previously known, good release.

!!! note
    All rollbacks create a new, numbered release. But will reference the build/code and configuration from the desired rollback point.


In this example, the application is currently running release v4. Using `deis rollback v2` tells Workflow to deploy the
build and configuration that was used for release v2. This creates a new release named v5 whose contents are the source
and configuration from release v2:

```
$ deis releases
=== folksy-offshoot Releases
v4      4 minutes ago                     gabrtv deployed d3ccc05
v3      1 hour 18 minutes ago             gabrtv added DATABASE_URL
v2      6 hours 2 minutes ago             gabrtv deployed 7cb3321
v1      6 hours 3 minutes ago             gabrtv deployed deis/helloworld

$ deis rollback v2
Rolled back to v2

$ deis releases
=== folksy-offshoot Releases
v5      Just now                          gabrtv rolled back to v2
v4      4 minutes ago                     gabrtv deployed d3ccc05
v3      1 hour 18 minutes ago             gabrtv added DATABASE_URL
v2      6 hours 2 minutes ago             gabrtv deployed 7cb3321
v1      6 hours 3 minutes ago             gabrtv deployed deis/helloworld
```

## Run One-off Administration Tasks

Deis applications [use one-off processes for admin tasks][] like database migrations and other commands that must run against the live application.

Use `deis run` to execute commands on the deployed application.

    $ deis run 'ls -l'
    Running `ls -l`...

    total 28
    -rw-r--r-- 1 root root  553 Dec  2 23:59 LICENSE
    -rw-r--r-- 1 root root   60 Dec  2 23:59 Procfile
    -rw-r--r-- 1 root root   33 Dec  2 23:59 README.md
    -rw-r--r-- 1 root root 1622 Dec  2 23:59 pom.xml
    drwxr-xr-x 3 root root 4096 Dec  2 23:59 src
    -rw-r--r-- 1 root root   25 Dec  2 23:59 system.properties
    drwxr-xr-x 6 root root 4096 Dec  3 00:00 target


## Share an Application

Use `deis perms:create` to allow another Deis user to collaborate on your application.

```
$ deis perms:create otheruser
Adding otheruser to peachy-waxworks collaborators... done
```

Use `deis perms` to see who an application is currently shared with, and `deis perms:remove` to remove a collaborator.

!!! note
    Collaborators can do anything with an application that its owner can do, except delete the application.

When working with an application that has been shared with you, clone the original repository and add Deis' git remote
entry before attempting to `git push` any changes to Deis.

```
$ git clone https://github.com/deis/example-java-jetty.git
Cloning into 'example-java-jetty'... done
$ cd example-java-jetty
$ git remote add -f deis ssh://git@local3.deisapp.com:2222/peachy-waxworks.git
Updating deis
From deis-controller.local:peachy-waxworks
 * [new branch]      master     -> deis/master
```


## Application Maintenance

Maintenance mode for applications is useful to perform certain migrations or upgrades during which we don't want to serve client requests. Deis Workflow supports maintenance mode for an app during which the access to the app is blocked. Blocking access to the application means all the requests to the app are served with an error code of `503` and a static maintenance page by the router but the app will still be running and one-off commands can still be run. Currently the maintenance page is not configurable and is present as part of the router component.

To enable maintenance mode for app, use `deis maintenance`:

    $ deis maintenance:on
    Enabling maintenance for drafty-zaniness... done

This will make the [router][] answer all requests to the application with a 503, although the app is still running. To disable maintenance mode:

    $ deis maintenance:off
    Disabling maintenance for drafty-zaniness... done


## Application Troubleshooting

Applications deployed on Deis Workflow [treat logs as event streams][]. Deis Workflow aggregates `stdout` and `stderr`
from every [Container][] making it easy to troubleshoot problems with your application.

Use `deis logs` to view the log output from your deployed application.

    $ deis logs | tail
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.5]: INFO:oejsh.ContextHandler:started o.e.j.s.ServletContextHandler{/,null}
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.8]: INFO:oejs.Server:jetty-7.6.0.v20120127
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.5]: INFO:oejs.AbstractConnector:Started SelectChannelConnector@0.0.0.0:10005
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.6]: INFO:oejsh.ContextHandler:started o.e.j.s.ServletContextHandler{/,null}
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.7]: INFO:oejsh.ContextHandler:started o.e.j.s.ServletContextHandler{/,null}
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.6]: INFO:oejs.AbstractConnector:Started SelectChannelConnector@0.0.0.0:10006
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.8]: INFO:oejsh.ContextHandler:started o.e.j.s.ServletContextHandler{/,null}
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.7]: INFO:oejs.AbstractConnector:Started SelectChannelConnector@0.0.0.0:10007
    Dec  3 00:30:31 ip-10-250-15-201 peachy-waxworks[web.8]: INFO:oejs.AbstractConnector:Started SelectChannelConnector@0.0.0.0:10008

[application]: ../reference-guide/terms.md#application
[container]: ../reference-guide/terms.md#container
[store config in environment variables]: http://12factor.net/config
[decoupled from the application]: http://12factor.net/backing-services
[scale out via the process model]: http://12factor.net/concurrency
[treat logs as event streams]: http://12factor.net/logs
[use one-off processes for admin tasks]: http://12factor.net/admin-processes
[Procfile]: http://ddollar.github.io/foreman/#PROCFILE
[router]: ../understanding-workflow/components.md#router
