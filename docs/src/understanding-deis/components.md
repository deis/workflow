# Components

Deis consists of a number of components that combine to create a distributed PaaS.
Each Deis component is deployed as a container or set of containers.

## Controller

The controller component is an HTTP API server. Among other functions, the
controller contains the scheduler, which decides where to run app containers.
The `deis` command-line client interacts with this component.

## Database

The database component is a [PostgreSQL][] server used to store durable
platform state. Backups and WAL logs are pushed to [Store][].

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

The store component uses [Ceph][] to store data for Deis components
which need to store state, including [Registry][], [Database][].

[Amazon S3]: http://aws.amazon.com/s3/
[Application]: ../reference-guide/terms.md#application
[Celery]: http://www.celeryproject.org/
[Config]: ../reference-guide/terms.md#config
[controller]: #controller
[Ceph]: http://ceph.com
[database]: #database
[Docker]: http://docker.io/
[Git]: http://git-scm.com/
[Nginx]: http://nginx.org/
[OpenStack Storage]: http://www.openstack.org/software/openstack-storage/
[PostgreSQL]: http://www.postgresql.org/
[Redis]: http://redis.io/
[registry]: #registry
[release]: ../reference-guide/terms.md#release
[router]: #router
[store]: #store
