# Components

Workflow is comprised of a number of small, independent services that combine
to create a distributed PaaS. All Workflow components are deployed as services
(and associated controllers) in your Kubernetes cluster. If you are interested
we have a more detailed exploration of the [Workflow
architecture][architecture.md].

All of the componentry for Workflow is built with composability in mind. If you
need to customize one of the components for your specific deployment or need
the functionality in your own project we invite you to give it a shot!

## Controller

Project Location: [deis/workflow](https://github.com/deis/workflow)

The controller component is an HTTP API server which serves as the endpoint for
the `deis` CLI. The controller provides all of the platform functionality as
well as interfacing with your Kubernetes cluster. The controller persists all
of its data to the database component.

## Database

Project Location: [deis/postgres](https://github.com/deis/postgres)

The database component is a managed instance of [PostgreSQL][] which holds a
majority of the platforms state. Backups and WAL files are pushed to the
[Store][] through [WAL-E][]. When the database is restarted, backups are
fetched and replayed from Store so no data is lost. For more information
on backup and restore read the documentation for
[Backing up and Restoring Data][backupandrestore].

## Builder

The builder component uses a [Git][] server to process
[Application][] builds. The builder:

1. Receives incoming `git push` requests over SSH
2. Authenticates the user via SSH key fingerprint
3. Authorizes the user's access to write to the Git repository
4. Builds a new `Docker` image from the updated git repository
5. Adds the latest [Config][] to the resulting Docker image
6. Pushes the new Docker image to the platform's [Registry][]
7. Triggers a new [Release][] through the [Controller][]

!!! note
    The builder component does not incorporate [Config][] directly into the images it produces. A [Release][] is a pairing of an application image with application configuration maintained separately in the Deis [Database][]. Once a new [Release][] is generated, a new set of containers is deployed across the platform automatically.

## Object Storage

Project Location: [deis/minio](https://github.com/deis/mino)

All of the Workflow components ship their persistent data to cluster configured
S3 compatibile Object Storage. For example, database ships its WAL files,
registry stores Docker images, and slugbuilder stores slugs.

Workflow supports either on or off-cluster storage. For production deployments
we highly recommend that you configure [off-cluster object storage][configure-objectstorage].

To facilitate experimentation, development and test environments, the default charts for
Workflow include on-cluster object storage via [minio](https://github.com/minio/minio).

If you also feel comforatable using Kubernetes persistent volumes you may
configure minio to use persistent storage available in your environment.

## Registry

Project Location: [deis/registry](https://github.com/deis/registry)

The registry component is a managed docker registry which holds application
images generated from the builder component. Registry persists the Docker image
iamges to either local storage (in development mode) or to object storage
configured for the cluster.

## Router

The router component uses [Nginx][] to route traffic to application containers.

[Amazon S3]: http://aws.amazon.com/s3/
[Application]: ../reference-guide/terms.md#application
[Celery]: http://www.celeryproject.org/
[Config]: ../reference-guide/terms.md#config
[Git]: http://git-scm.com/
[Minio]: https://www.minio.io/
[Nginx]: http://nginx.org/
[OpenStack Storage]: http://www.openstack.org/software/openstack-storage/
[PostgreSQL]: http://www.postgresql.org/
[Redis]: http://redis.io/
[WAL-E]: https://github.com/wal-e/wal-e
[architecture]: architecture.md
[backupandrestore]: ../managing-deis/backing-up-and-restoring-data.md
[configure-objectstorage]: ../installing-deis/configuring-object-storage.md
[controller]: #controller
[database]: #database
[registry]: #registry
[release]: ../reference-guide/terms.md#release
[router]: #router
[store]: #store
