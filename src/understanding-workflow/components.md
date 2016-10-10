# Components

Workflow is comprised of a number of small, independent services that combine
to create a distributed PaaS. All Workflow components are deployed as services
(and associated controllers) in your Kubernetes cluster. If you are interested
we have a more detailed exploration of the [Workflow
architecture][architecture].

All of the componentry for Workflow is built with composability in mind. If you
need to customize one of the components for your specific deployment or need
the functionality in your own project we invite you to give it a shot!

## Controller

**Project Location:** [deis/controller](https://github.com/deis/controller)

The controller component is an HTTP API server which serves as the endpoint for
the `deis` CLI. The controller provides all of the platform functionality as
well as interfacing with your Kubernetes cluster. The controller persists all
of its data to the database component.

## Database

**Project Location:** [deis/postgres](https://github.com/deis/postgres)

The database component is a managed instance of [PostgreSQL][] which holds a
majority of the platforms state. Backups and WAL files are pushed to object
storage via [WAL-E][]. When the database is restarted, backups are fetched and
replayed from object storage so no data is lost.

## Builder: builder, slugbuilder, and dockerbuilder

**Project Location:** [deis/builder](https://github.com/deis/builder)


The builder component is responsible for accepting code pushes via [Git][] and
managing the build process of your [Application][]. The builder process is:

1. Receives incoming `git push` requests over SSH
2. Authenticates the user via SSH key fingerprint
3. Authorizes the user's access to push code to the Application
4. Starts the Application Build phase (see below)
5. Triggers a new [Release][] via the Controller

Builder currently supports both buildpack and Dockerfile based builds.

**Project Location:** [deis/slugbuilder](https://github.com/deis/slugbuilder)

For Buildpack-based deploys, the builder component will launch a one-shot Pod
in the `deis` namespace. This pod runs `slugbuilder` component which handles
default and custom buildpacks (specified by `BUILDPACK_URL`). The "compiled"
application results in a slug, consisting of your application code and all of
its dependencies as determined by the buildpack. The slug is pushed to the
cluster-configured object storage for later execution. For more information
about buildpacks see [using buildpacks][using-buildpacks].

**Project Location:** [deis/dockerbuilder](https://github.com/deis/dockerbuilder)

For Applications which contain a `Dockerfile` in the root of the repository,
`builder` will instead launch the `dockerbuilder` to package your application.
Instead of generating a slug, `dockerbuilder` generates a Docker image (using
the underlying Docker engine). The completed image is pushed to the managed
Docker registry on cluster. For more information see [using Dockerfiles][using-dockerfiles].

## Slugrunner

**Project Location:** [deis/slugrunner](https://github.com/deis/slugrunner)

Slugrunner is the component responsible for executing buildpack-based
Applications. Slugrunner receives slug information from the controller and
downloads the application slug just before launching your application
processes.

## Object Storage

**Project Location:** [deis/minio](https://github.com/deis/minio)

All of the Workflow components that need to persist data will ship them to the
object storage that was configured for the cluster.For example, database ships
its WAL files, registry stores Docker images, and slugbuilder stores slugs.

Workflow supports either on or off-cluster storage. For production deployments
we highly recommend that you configure [off-cluster object storage][configure-objectstorage].

To facilitate experimentation, development and test environments, the default charts for
Workflow include on-cluster object storage via [minio](https://github.com/minio/minio).

If you also feel comfortable using Kubernetes persistent volumes you may
configure minio to use persistent storage available in your environment.

## Registry

**Project Location:** [deis/registry](https://github.com/deis/registry)

The registry component is a managed docker registry which holds application
images generated from the builder component. Registry persists the Docker image
images to either local storage (in development mode) or to object storage
configured for the cluster.

## Router

**Project Location:** [deis/router](https://github.com/deis/router)

The router component is based on [Nginx][] and is responsible for routing
inbound HTTP(S) traffic to your applications. The default workflow charts
provision a Kubernetes service in the `deis` namespace with a service type of
`LoadBalancer`. Depending on your Kubernetes configuration, this may provision
a cloud-based loadbalancer automatically.

The router component uses Kubernetes annotations for both Application discovery
as well as router configuration. For more detailed documentation and possible
configuration view the router [project documentation][router-documentation].

## Logger: fluentd, logger

The logging subsystem consists of two components. Fluentd handles log shipping
and logger maintains a ring-buffer of application logs.


**Project Location:** [deis/fluentd](https://github.com/deis/fluentd)

Fluentd is deployed to your Kubernetes cluster via Daemon Sets. Fluentd
subscribes to all container logs, decorates the output with Kubernetes metadata
and can be configured to drain logs to multiple destinations. By default,
fluentd ships logs to the logger component, which powers `deis logs`.

**Project Location:** [deis/logger](https://github.com/deis/logger)

The `logger` component receives log streams from `fluentd`, collating by
Application name. Logger does not persist logs to disk, instead maintaining an
in-memory ring buffer. For more information on logger see the [project
documentation][logger-documentation].

## See Also

* [Workflow Concepts][concepts]
* [Workflow Architecture][architecture]

[Application]: ../reference-guide/terms.md#application
[Config]: ../reference-guide/terms.md#config
[Git]: http://git-scm.com/
[Nginx]: http://nginx.org/
[PostgreSQL]: http://www.postgresql.org/
[WAL-E]: https://github.com/wal-e/wal-e
[architecture]: architecture.md
[concepts]: concepts.md
[configure-objectstorage]: ../installing-workflow/configuring-object-storage.md
[logger-documentation]: https://github.com/deis/logger
[release]: ../reference-guide/terms.md#release
[router-documentation]: https://github.com/deis/router
[router]: #router
[using-buildpacks]: ../applications/using-buildpacks.md
[using-dockerfiles]: ../applications/using-dockerfiles.md
