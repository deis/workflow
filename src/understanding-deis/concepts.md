# Concepts

Deis Workflow is a lightweight application platform that deploys and scales
Twelve-Factor apps as containers across a Kubernetes cluster.

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
the activity on your cluster, including: desired state convergence, stable
service addresses, health monitoring, service discovery, and DNS resolution.

Workflow builds upon Kubernetes abstractions like Services, Replication
Controllers and Pods to provide a developer-friendly UX, source to image, log
aggregation, etc.

Workflow is shipped as a Kubernetes-native application, installable via
[Helm][helm]. So operators familiar with Kubernetes will feel right at home
running Workflow.

For a detailed overview of Workflow components, see our [component][components] break down.

## Docker

[Docker][] is an open source project to build, ship and run any
application as a lightweight, portable, self-sufficient container.

If you have not yet converted your application to containers, Workflow provides
a simple and straightforward "source to Docker image" capability. Supporting
multiple language runtimes via community [buildpacks][], building your application
in a container can be as easy as `git push deis master`.

Applications which are packaged via a buildpack are run in Docker containers as
part of the `slugrunner` process. View the [slugrunner compoent][slugrunner]
for more information.

Applications which use either a Dockerfile or reference an external Docker
Image are launched unmodified.

## Applications

Workflow is designed around the concept of an [application][], or app.

Applications can come in three forms:

1. as collection of source files stored in a Git repository
2. as a Dockerfile, which describes how to build your app
3. a reference to an already built Docker Image, hosted on a remote Docker repository

Applications are always given a unique name for easy reference. Workflow also
tracks other related information for your application including any domain
names, SSL Certificates and developer provided configuration.

## Build, Release, Run

![Deis Git Push Workflow](DeisGitPushWorkflow.png)

### Build Stage

The [builder][] component processes incoming `git push deis master` requests
manages your application packaging.

If your application is using a [buildpack][] builder will launch an ephemeral
job to extract and execute the packaging instructions. The resulting
application artifact is stored by the platform for execution during the run
stage.

Instead, if you provide a [Dockerfile][dockerfile] builder will use the
instructions you've provided to build a Docker Image. The resulting artifact is
stored in a Deis-managed registry which will be referenced during the run
stage.

If you already have an external system building your application container you
can simply reference that artifact. When using [external Docker
images][dockerimage] the builder component doesn't attempt to repackage your
app.

### Release Stage

During the release stage, a [build][] is combined with [application configuration][config]
to create a new numbered [release][]. New releases are created any time a new
build is created or application configuration is changed. Tracking releases
makes it easy to rollback to any previous release.

### Run Stage

The run stage is responsible for deploying the new release to the underlying
Kubernetes cluster. The run stage launches a new Replication Controller which
references the new release. By managing the desired replica count, Workflow
orchestrates a zero-downtime, rolling update of your application. Once
successfully updated, Workflow removes the last reference to the old release.
Note that during the deploy, your application will be running in a mixed mode.

## Backing Services

Workflow treats all persistent serivces such as databases, caches, storage,
messaging systems, and other [backing services][] as resources managed
separtely from your application. This philosophy aligns with Twelve-Factor
best practices.

Applications are attached to backing services using [environment variables][].
Because applications are decoupled from backing services, apps are free to
scale up independently, to swap services provided by other apps, or to switch
to external or third-party vendor services.

## See Also

* [Architecture](architecture.md)
* [Twelve-Factor App][]

[Build and Run]: http://12factor.net/build-release-run
[Docker]: https://www.docker.com/
[Kubernetes]: https://kubernetes.io
[Twelve-Factor App]: http://12factor.net/
[application]: ../reference-guide/terms.md#application
[backing services]: http://12factor.net/backing-services
[build]: ../reference-guide/terms.md#build
[builder]: components.md#builder
[buildpacks]: ../using-deis/using-buildpacks.md
[cncf]: https://cncf.io/
[components]: components.md
[config]: ../reference-guide/terms.md#config
[dockerfile]: ../using-deis/using-dockerfiles.md
[dockerimage]: ../using-deis/using-docker-images.md
[environment variables]: http://12factor.net/config
[helm]: https://helm.sh
[release]: ../reference-guide/terms.md#release
[slugrunner]: concepts.md#slugrunner
