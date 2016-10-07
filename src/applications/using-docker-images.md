# Using Docker Images

Deis supports deploying applications via an existing [Docker Image][].
This is useful for integrating Deis into Docker-based CI/CD pipelines.


## Prepare an Application

Start by cloning an example application:

    $ git clone https://github.com/deis/example-dockerfile-http.git
    $ cd example-dockerfile-http

Next use your local `docker` client to build the image and push
it to [DockerHub][].

    $ docker build -t <username>/example-dockerfile-http .
    $ docker push <username>/example-dockerfile-http


### Docker Image Requirements

In order to deploy Docker images, they must conform to the following requirements:

* The Dockerfile must use the `EXPOSE` directive to expose exactly one port.
* That port must be listening for an HTTP connection.
* The Dockerfile must use the `CMD` directive to define the default process that will run within the container.
* The Docker image must contain [bash](https://www.gnu.org/software/bash/) to run processes.

!!! note
    Note that if you are using a private registry of any kind (`gcr` or other) the application environment must include a `$PORT` config variable that matches the `EXPOSE`'d port, example: `deis config:set PORT=5000`. See [Configuring Registry](../installing-workflow/configuring-registry/#configuring-off-cluster-private-registry) for more info.

## Create an Application

Use `deis create` to create an application on the [controller][].

    $ mkdir -p /tmp/example-dockerfile-http && cd /tmp/example-dockerfile-http
    $ deis create example-dockerfile-http --no-remote
    Creating application... done, created example-dockerfile-http

!!! note
    For all commands except for `deis create`, the `deis` client uses the name of the current directory
    as the app name if you don't specify it explicitly with `--app`.


## Deploy the Application

Use `deis pull` to deploy your application from [DockerHub][] or
a public registry.

    $ deis pull <username>/example-dockerfile-http:latest
    Creating build...  done, v2

    $ curl -s http://example-dockerfile-http.local3.deisapp.com
    Powered by Deis

Because you are deploying a Docker image, the `cmd` process type is automatically scaled to 1 on first deploy.

Use `deis scale cmd=3` to increase `cmd` processes to 3, for example. Scaling a
process type directly changes the number of [Containers][container]
running that process.

## Private Registry

To deploy Docker images from a private registry or from a private repository, use `deis registry`
to attach credentials to your application. These credentials are the same as you'd use when running
`docker login` at your private registry.

To deploy private Docker images, take the following steps:

* Gather the username and password for the registry, such as a [Quay.io Robot Account][] or a [GCR.io Long Lived Token][]
* Run `deis registry:set username=<the-user> password=<secret> -a <application-name>`
* Now perform `deis pull` as normal, against an image in the private registry

When using a [GCR.io Long Lived Token][], the JSON blob will have to be compacted first using a
tool like [jq][] and then used in the password field in `deis registry:set`. For the username, use
`_json_key`. For example:

```
deis registry:set username=_json_key password="$(cat google_cloud_cred.json | jq -c .)"
```

When using a private registry the docker images are no longer pulled into the Deis Internal Registry via
the Deis Workflow Controller but rather is managed by Kubernetes. This will increase security and overall speed,
however the application `port` information can no longer be discovered. Instead the application `port` information can be set via
`deis config:set PORT=80` prior to setting the registry information.

!!! note
    Currently [GCR.io][] and [ECR][] in short lived auth token mode are not supported.

[container]: ../reference-guide/terms.md#container
[controller]: ../understanding-workflow/components.md#controller
[Docker Image]: https://docs.docker.com/introduction/understanding-docker/
[DockerHub]: https://registry.hub.docker.com/
[CMD instruction]: https://docs.docker.com/reference/builder/#cmd
[Quay.io Robot Account]: https://docs.quay.io/glossary/robot-accounts.html
[GCR.io Long Lived Token]: https://cloud.google.com/container-registry/docs/auth#using_a_json_key_file
[jq]: https://stedolan.github.io/jq/
[GCR.io]: https://gcr.io
[ECR]: https://aws.amazon.com/ecr/
