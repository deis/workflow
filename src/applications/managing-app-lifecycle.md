# Managing an Application

## Scaling an Application

Applications deployed on Deis [scale out via the process model][]. Use `deis scale` to control the number of
[Containers][container] that power your app.

```
$ deis scale cmd=5 -a iciest-waggoner
Scaling processes... but first, coffee!
done in 3s
=== iciest-waggoner Processes
--- cmd:
iciest-waggoner-v2-cmd-09j0o up (v2)
iciest-waggoner-v2-cmd-3r7kp up (v2)
iciest-waggoner-v2-cmd-gc4xv up (v2)
iciest-waggoner-v2-cmd-lviwo up (v2)
iciest-waggoner-v2-cmd-kt7vu up (v2)
```

If you have multiple process types for your application you may scale the process count for each type separately. For
example, this allows you to manage web process indepenetly from background workers. For more information on process
types see our documentation for [Managing App Processes](managing-app-processes.md).

In this example, we are scaling the process type `web` to 5 but leaving the process type `background` with one worker.

```
$ deis scale web=5
Scaling processes... but first, coffee!
done in 4s
=== scenic-icehouse Processes
--- web:
scenic-icehouse-v2-web-7lord up (v2)
scenic-icehouse-v2-web-jn957 up (v2)
scenic-icehouse-v2-web-rsekj up (v2)
scenic-icehouse-v2-web-vwhnh up (v2)
scenic-icehouse-v2-web-vokg7 up (v2)
--- background:
scenic-icehouse-v2-background-yf8kh up (v2)
```

!!! note
    The default process type for Dockerfile and Docker Image applications is 'cmd' rather than 'web'.

Scaling a process down, by reducing the process count, sends a `TERM` signal to the processes, followed by a `SIGKILL`
if they have not exited within 30 seconds. Depending on your application, scaling down may interrupt long-running HTTP
client connections.

For example, scaling from 5 processes to 3:

```
$ deis scale web=3
Scaling processes... but first, coffee!
done in 1s
=== scenic-icehouse Processes
--- background:
scenic-icehouse-v2-background-yf8kh up (v2)
--- web:
scenic-icehouse-v2-web-7lord up (v2)
scenic-icehouse-v2-web-rsekj up (v2)
scenic-icehouse-v2-web-vokg7 up (v2)
```

## Restarting an Application Processes

If you need to restart an application process, you may use `deis ps:restart`. Behind the scenes, Deis Workflow instructs
Kubernetes to terminate the old process and launch a new one in its place.

```
$ deis ps
=== scenic-icehouse Processes
--- web:
scenic-icehouse-v2-web-7lord up (v2)
scenic-icehouse-v2-web-rsekj up (v2)
scenic-icehouse-v2-web-vokg7 up (v2)
--- background:
scenic-icehouse-v2-background-yf8kh up (v2)
$ deis ps:restart scenic-icehouse-v2-background-yf8kh
Restarting processes... but first, coffee!
done in 6s
=== scenic-icehouse Processes
--- background:
scenic-icehouse-v2-background-yd87g up (v2)
```

Notice that the process name has changed from `scenic-icehouse-v2-background-yf8kh` to
`scenic-icehouse-v2-background-yd87g`. In a multi-node Kubernetes cluster, this may also have the effect of scheduling
the Pod to a new node.

## Track Application Changes

Deis Workflow tracks all changes to your application. Application changes are the result of either new application code
pushed to the platform (via `git push deis master`), or an update to application configuration (via `deis config:set KEY=VAL`).

Each time a build or config change is made to your application a new [release][] is created. These release numbers
increase montonically.

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
