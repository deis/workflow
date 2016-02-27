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
majority of the platforms state. Backups and WAL logs are pushed to the
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

## Registry

The registry component hosts [Docker][] images on behalf of the platform.
Image data is stored by [Store][].

## Router

The router component uses [Nginx][] to route traffic to application containers.

## Store

The Store component uses [Minio][] by default to store data for Deis components which need to store
state, including the [Registry][] and the [Database][].

If you are using Minio as the Store, it is highly recommended that the Store's data is backed by a
persistent volume in the event of complete failure. See
[Backing up and Restoring Data](../managing-deis/backing-up-and-restoring-data.md) for more
information.

[Amazon S3]: http://aws.amazon.com/s3/
[Application]: ../reference-guide/terms.md#application
[Celery]: http://www.celeryproject.org/
[Config]: ../reference-guide/terms.md#config
[controller]: #controller
[database]: #database
[Docker]: http://docker.io/
[Git]: http://git-scm.com/
[Minio]: https://www.minio.io/
[Nginx]: http://nginx.org/
[OpenStack Storage]: http://www.openstack.org/software/openstack-storage/
[PostgreSQL]: http://www.postgresql.org/
[Redis]: http://redis.io/
[registry]: #registry
[release]: ../reference-guide/terms.md#release
[router]: #router
[store]: #store
[WAL-E]: https://github.com/wal-e/wal-e
