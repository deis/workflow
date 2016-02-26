# Concepts

Deis is a lightweight application platform that deploys and scales Twelve-Factor apps as Docker containers across a cluster of Kubernetes minions.

## Twelve-Factor Applications

The [Twelve-Factor App][] is a methodology for building modern
applications that can be scaled across a distributed system.

We consider it an invaluable synthesis of much experience with
software-as-a-service apps in the wild, especially on the
Heroku platform.

Workflow is designed to run applications that adhere to [Twelve-Factor App][]
methodology and best practices.

## Kubernetes

[Kubernetes][] is an open-source cluster manager developed by Google and
donated to the [Cloud Native Compute Foundation][cncf]. Kubernetes manages all
the activity on your cluster. Including converging to a desired state,
providing critical functions like stable service addresses, health monitoring,
service discovery and DNS resolution.

Workflow builds upon Kubernetes abstractions like Services, Replication
Controllers and Pods to provide a developer-friendly UX, source to image, log
aggregation, etc.

Workflow is shipped as a Kubernetes-native application, installable via
[Helm][helm]. So operators familiar with Kubernetes will feel right at home
running Workflow.

For a detailed overview of Workflow components, see our [component][] break down.

## Docker

[Docker][] is an open source project to build, ship and run any
application as a lightweight, portable, self-sufficient container.

Workflow uses Docker Images and the Docker Engine (via Kubernetes) to package
and run your application respectively.

If you have not yet converted your application to containers, Workflow provides
a simple and straightforward "source to Docker image" capability. Supporting
multiple language runtimes via community [buildpacks][], building your application
in a container can be as easy as `git push deis master`.

## Applications

Workflow is designed around the concept of an [application][], or app.

Applications can come in three forms. First, as collection of source files
stored in a Git repository. Second, as a Dockerfile, which describes how to
build your app. Third, a reference to an already built Docker Image, hosted on
a remote repository.

Applications are always given a unique name for easy reference. Workflow also
tracks other related information for your application including any domain
names, SSL Certificates and developer provided configuration.

## Build, Release, Run

![Deis Git Push Workflow](DeisGitPushWorkflow.png)

### Build Stage

The [builder][] processes incoming `git push` requests and builds applications
inside ephemeral Docker containers, resulting in a new Docker image.

### Release Stage

During the release stage, a [build][] is combined with [config][] to create a new numbered
[release][]. This release is then pushed to a Docker registry for later execution.
The release stage is triggered any time a new build is created or config is
changed, making it easy to rollback code and configuration changes.

### Run Stage

The run stage dispatches containers to a scheduler and updates the router accordingly.
The scheduler is in control of placing containers on hosts and balancing them evenly across the cluster.
Containers are published to the router once they are healthy.  Old containers are only collected
after the new containers are live and serving traffic -- providing zero-downtime deploys.

## Backing Services

Deis treats databases, caches, storage, messaging systems, and other
[backing services][] as attached resources, in keeping with Twelve-Factor
best practices.

Applications are attached to backing services using [environment variables][].
Because applications are decoupled from backing services, apps are free to scale up independently,
to swap services provided by other apps, or to switch to external or third-party vendor services.

## See Also

* [Architecture](architecture.md)
* [Twelve-Factor App][]


[application]: ../reference-guide/terms.md#application
[build]: ../reference-guide/terms.md#build
[builder]: components.md#builder
[config]: ../reference-guide/terms.md#config
[Docker]: https://www.docker.com/
[Build and Run]: http://12factor.net/build-release-run
[backing services]: http://12factor.net/backing-services
[environment variables]: http://12factor.net/config
[release]: ../reference-guide/terms.md#release
[Twelve-Factor App]: http://12factor.net/
[Kubernetes]: https://kubernetes.io
[cncf]: https://cncf.io/
[helm]: https://helm.sh
[components]: components.md
[buildpacks]: ../using-deis/using-buildpacks.md
