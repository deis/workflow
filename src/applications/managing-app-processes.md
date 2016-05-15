# Managing Application Processes

Deis Workflow manages your application as a set of processes that can be named, scaled and configured according to their
role. This gives you the flexiblity to easily manage the different facets of your application. For example, you may have
web-facing processes that handle HTTP traffic, background worker processes that do async work, and a helper process that
streams from the Twitter API.

By using a Procfile, either checked in to your application or provided via the CLI you can specify the name of the type
and the application command that should run. To spawn other process types, use `deis scale <type>=<n>` to scale those
types accordingly.

## Default Process Types

In the absence of a Procfile, a single, default process type is assumed for each application.

Applications built using [Buildpacks][buildpacks] via `git push` implicitly receive a `web` process type, which starts
the application server. Rails 4, for example, has the following process type:

    web: bundle exec rails server -p $PORT

All applications utilizing [Dockerfiles][dockerfile] have an implied `cmd` process type, which runs the
Dockerfile's `CMD` directive unmodified:

    $ cat Dockerfile
    FROM centos:latest
    COPY . /app
    WORKDIR /app
    CMD python -m SimpleHTTPServer 5000
    EXPOSE 5000

For the above Dockerfile-based application, the `cmd` process type would run the Docker `CMD` of `python -m SimpleHTTPServer 5000`.

Applications utilizing [remote Docker images][docker image], a `cmd` process type is also implied, and runs the `CMD`
specified in the Docker image.

!!! note
    The `web` and `cmd` process types are special as they’re the only process types that will
    receive HTTP traffic from Workflow’s routers. Other process types can be named arbitrarily.

## Declaring Process Types

If you use [Buildpack][buildpacks] or [Dockerfile][dockerfile] builds and want to override or specify additional process
types, simply include a file named `Procfile` in the root of your application's source tree.

The format of a `Procfile` is one process type per line, with each line containing the command to invoke:

    <process type>: <command>

The syntax is defined as:

* `<process type>` – an alphanumeric string, is a name for your command, such as web, worker, urgentworker, clock, etc.
* `<command>` – a command line to launch the process, such as `rake jobs:work`.

This example Procfile specifies two types, `web` and `sleeper`. The `web` process launches a web server on port 5000 and
a simple process which sleeps for 900 seconds and exits.

```
$ cat Procfile
web: bundle exec ruby web.rb -p ${PORT:-5000}
sleeper: sleep 900
```

If you are using [remote Docker images][docker image], you may define process types by either running `deis pull` with a
`Procfile` in your working directory, or by passing a stringified Procfile to the `--procfile` CLI option.

For example:

```
$ deis pull deis/example-go:latest --procfile="cmd: /app/bin/boot"
```

Or via a Procfile:

```
$ cat Procfile
cmd: /bin/boot
sleeper: echo "sleeping"; sleep 900
$ deis pull -a steely-mainsail deis/example-go
Creating build... done
$ deis scale sleeper=1 -a steely-mainsail
Scaling processes... but first, coffee!
done in 0s
=== steely-mainsail Processes
--- cmd:
steely-mainsail-v3-cmd-nyrim up (v3)
--- sleeper:
steely-mainsail-v3-sleeper-oq1jr up (v3)
```

!!! note
    Only process types of `web` and `cmd` will be scaled to 1 automatically. If you have additional process types
    remember to scale the process counts after creation.

To remove a process type simply scale it to 0:

```
$ deis scale sleeper=0 -a steely-mainsail
Scaling processes... but first, coffee!
done in 3s
=== steely-mainsail Processes
--- cmd:
steely-mainsail-v3-cmd-nyrim up (v3)
```

## Scaling Processes

Applications deployed on Deis Workflow [scale out via the process model][]. Use `deis scale` to control the number of
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

## Web vs Cmd Process Types

When deploying to Deis Workflow using a Heroku Buildpack, Workflow boots the `web` process type to
boot the application server. When you deploy an application that has a Dockerfile or uses [Docker
images][docker image], Workflow boots the `cmd` process type. Both act similarly in that
they are exposed to the router as web applications. However, the `cmd` process type is special
because, if left undefined, it is equivalent to running the [container][] without any additional
arguments.  (i.e. The process specified by the Dockerfile or Docker image's `CMD` directive will
be used.)

If migrating an application from Heroku Buildpacks to a Docker-based deployment, Workflow will not
automatically convert the `web` process type to `cmd`. To do this, you'll have to manually scale
down the old process type and scale the new process type up.

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

[container]: ../reference-guide/terms.md#container
[process model]: https://devcenter.heroku.com/articles/process-model
[buildpacks]: ../applications/using-buildpacks.md
[dockerfile]: ../applications/using-dockerfiles.md
[docker image]: ../applications/using-docker-images.md
