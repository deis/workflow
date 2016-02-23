# Process Types and the Procfile

A Procfile is a mechanism for declaring what commands are run by your application’s containers on
the Deis platform. It follows the [process model][]. You can use a Procfile to declare various
process types, such as multiple types of workers, a singleton process like a clock, or a consumer
of the Twitter streaming API.

## Process Types as Templates

A Procfile is a text file named `Procfile` placed in the root of your application that lists the
process types in an application. Each process type is a declaration of a command that is executed
when a container of that process type is started.

All the language and frameworks using [Heroku's Buildpacks](using-buildpacks.md) declare a
`web` process type, which starts the application server. Rails 3 has the following process type:

    web: bundle exec rails server -p $PORT

All applications using [Dockerfile deployments](using-dockerfiles.md) have an implied `cmd`
process type, which spawns the default process of a Docker image:

    $ cat Dockerfile
    FROM centos:latest
    COPY . /app
    WORKDIR /app
    CMD python -m SimpleHTTPServer 5000
    EXPOSE 5000

For applications using [Docker image deployments](using-docker-images.md), a `cmd` process
type is also implied and spawns the default process of the image.


## Declaring Process Types

Process types are declared via a file named `Procfile`, placed in the root of your app. Its
format is one process type per line, with each line containing:

    <process type>: <command>

The syntax is defined as:

`<process type>` – an alphanumeric string, is a name for your command, such as web, worker, urgentworker, clock, etc.

`<command>` – a command line to launch the process, such as `rake jobs:work`.

!!! note
    The web and cmd process types are special as they’re the only process types that will receive
    HTTP traffic from Deis’s routers. Other process types can be named arbitrarily.


## Deploying to Deis

A `Procfile` is not necessary to deploy most languages supported by Deis. The platform
automatically detects the language and supplies a default `web` process type to boot the server.

Creating an explicit Procfile is recommended for greater control and flexibility over your app.

For Deis to use your Procfile, add the Procfile to the root of your application, then push to Deis:

    $ git add .
    $ git commit -m "Procfile"
    $ git push deis master
    ...
    -----> Procfile declares process types: web, worker
    Compiled slug size is 10.4MB

           Launching... done, v2

    -----> unisex-huntress deployed to Deis
           http://unisex-huntress.example.com

For Docker image deployments, a Procfile in the current directory or specified by
`deis pull --procfile` will define the default process types for the application.

Use `deis scale web=3` to increase `web` processes to 3, for example. Scaling a
process type directly changes the number of [Containers][container]
running that process.


## Web vs Cmd Process Types

When deploying to Deis using a Heroku Buildpack, Deis boots the `web` process type to boot the
application server. When you deploy an application that has a Dockerfile or uses [Docker
images](using-docker-images.md), Deis boots the `cmd` process type. Both act similarly in that they
are exposed to the router as web applications. However, The `cmd` process type is special because
it is equivalent to running the [container][] without any additional arguments. Every other
process type is equivalent to running the relevant command that is provided in the Procfile.

When migrating from Heroku Buildpacks to a Docker-based deployment, Deis will not convert `web`
process types to `cmd`. To do this, you'll have to manually scale down the old process type and
scale the new process type up.

[container]: ../reference-guide/terms.md#container
[process model]: https://devcenter.heroku.com/articles/process-model
