# Managing Application Processes

Deis Workflow manages your application as a set of processes that can be named, scaled and configured according to their
role. This gives you the flexibility to easily manage the different facets of your application. For example, you may have
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
steely-mainsail-cmd-3291896318-nyrim up (v3)
--- sleeper:
steely-mainsail-sleeper-3291896318-oq1jr up (v3)
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
steely-mainsail-cmd-3291896318-nyrim up (v3)
```

## Scaling Processes

Applications deployed on Deis Workflow scale out via the [process model][]. Use `deis scale` to control the number of
[containers][container] that power your app.

```
$ deis scale cmd=5 -a iciest-waggoner
Scaling processes... but first, coffee!
done in 3s
=== iciest-waggoner Processes
--- cmd:
iciest-waggoner-web-3291896318-09j0o up (v2)
iciest-waggoner-web-3291896318-3r7kp up (v2)
iciest-waggoner-web-3291896318-gc4xv up (v2)
iciest-waggoner-web-3291896318-lviwo up (v2)
iciest-waggoner-web-3291896318-kt7vu up (v2)
```

If you have multiple process types for your application you may scale the process count for each type separately. For
example, this allows you to manage web process independently from background workers. For more information on process
types see our documentation for [Managing App Processes](managing-app-processes.md).

In this example, we are scaling the process type `web` to 5 but leaving the process type `background` with one worker.

```
$ deis scale web=5
Scaling processes... but first, coffee!
done in 4s
=== scenic-icehouse Processes
--- web:
scenic-icehouse-web-3291896318-7lord up (v2)
scenic-icehouse-web-3291896318-jn957 up (v2)
scenic-icehouse-web-3291896318-rsekj up (v2)
scenic-icehouse-web-3291896318-vwhnh up (v2)
scenic-icehouse-web-3291896318-vokg7 up (v2)
--- background:
scenic-icehouse-web-3291896318-background-yf8kh up (v2)
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
scenic-icehouse-web-3291896318-background-yf8kh up (v2)
--- web:
scenic-icehouse-web-3291896318-7lord up (v2)
scenic-icehouse-web-3291896318-rsekj up (v2)
scenic-icehouse-web-3291896318-vokg7 up (v2)
```

## Autoscale

Autoscale allows adding a minimum and maximum number of pods on a per process type basis. This is accomplished by specifying a target CPU usage across all available pods.

This feature is built on top of [Horizontal Pod Autoscaling][HPA] in Kubernetes or [HPA][] for short.

!!! note
	This is an alpha feature. It is recommended to be on the latest Kubernetes when using this feature.

```
$ deis autoscale:set web --min=3 --max=8 --cpu-percent=75
Applying autoscale settings for process type web on scenic-icehouse... done

```
And then review the scaling rule that was created for `web`

```
$ deis autoscale:list
=== scenic-icehouse Autoscale

--- web:
Min Replicas: 3
Max Replicas: 8
CPU: 75%
```

Remove scaling rule

```
$ deis autoscale:unset web
Removing autoscale for process type web on scenic-icehouse... done
```

For autoscaling to work CPU requests have to be specified on each application Pod (can be done via `deis limits --cpu`). This allows the autoscale policies to do the [appropriate calculations][autoscale-algo] and make decisions on when to scale up and down.

Scale up can only happen if there was no rescaling within the last 3 minutes. Scale down will wait for 5 minutes from the last rescaling. That information and more can be found at [HPA algorithm page][autoscale-algo].


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
scenic-icehouse-web-3291896318-7lord up (v2)
scenic-icehouse-web-3291896318-rsekj up (v2)
scenic-icehouse-web-3291896318-vokg7 up (v2)
--- background:
scenic-icehouse-background-3291896318-yf8kh up (v2)
$ deis ps:restart scenic-icehouse-background-3291896318-yf8kh
Restarting processes... but first, coffee!
done in 6s
=== scenic-icehouse Processes
--- background:
scenic-icehouse-background-3291896318-yd87g up (v2)
```

Notice that the process name has changed from `scenic-icehouse-background-3291896318-yf8kh` to
`scenic-icehouse-background-3291896318-yd87g`. In a multi-node Kubernetes cluster, this may also have the effect of scheduling
the Pod to a new node.

[container]: ../reference-guide/terms.md#container
[process model]: https://devcenter.heroku.com/articles/process-model
[buildpacks]: ../applications/using-buildpacks.md
[dockerfile]: ../applications/using-dockerfiles.md
[docker image]: ../applications/using-docker-images.md
[HPA]: http://kubernetes.io/docs/user-guide/horizontal-pod-autoscaling/
[autoscale-algo]: https://github.com/kubernetes/kubernetes/blob/master/docs/design/horizontal-pod-autoscaler.md#autoscaling-algorithm
