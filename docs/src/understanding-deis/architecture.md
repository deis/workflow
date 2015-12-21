# Architecture

Deis uses a service oriented architecture with [components][]
grouped into a Control Plane, Data Plane and Router Mesh.

## System Diagram

![Deis System Diagram](DeisSystemDiagram.png)

Operators use the `Deisctl API` to stand up the cluster's Control Plane, Data Plane and Router Mesh.
End-users of the platform interact with the Control Plane using the `Deis API`.

The Control Plane dispatches work to the Data Plane via a scheduler.
The Router Mesh is used to route traffic to both the Control Plane and Data Plane.
Because the router mesh is usually connected to the public Internet,
it is often connected to a front-end load balancer.

## Control Plane

![Deis Control Plane Architecture](DeisControlPlane.png)

The Control Plane performs management functions for the platform.
Control plane components (in blue) are all implemented as Docker containers.

The [store][] component consists of a number of smaller components that represent a
containerized Ceph cluster which provides a blob storage API and POSIX filesystem API
for the control plane's stateful components:

 * [registry][] - a Docker registry used to hold images and configuration data
 * [database][] - a Postgres database used to store platform state
 * [logger][] - a syslog log server that holds aggregated logs from the data plane

End-users interact primarily with the [controller][] which exposes an
HTTP API. They can also interact with the [builder][] via `git push`.

## Data Plane

![Deis Data Plane Architecture](DeisDataPlane.png)

The Data Plane is where [containers][] (in blue) are run on behalf of end-users.

The platform scheduler is in charge of placing containers on hosts in the data plane.
Deis also requires a few lightweight components on these hosts:

 * [publisher][] - publishes end-user containers to the [router][]

## Router Mesh

![Deis Router Mesh Architecture](DeisRouterMesh.png)

The Router Mesh publishes [Applications][] to consumers.

Each [router][] in the mesh is a configurable software load balancer designed to expose
[containers][] running in the data plane.
Routers track healthy containers using a distributed, watchable store like `etcd`.

Any changes to router configuration or certificates are applied within seconds.

## Topologies

For small deployments you can run the entire platform
-- Control Plane, Data Plane and Router Mesh -- on just 3 servers.

For larger deployments, you'll want to isolate the Control Plane and Router
Mesh, then scale your Data Plane out to as many servers as you need.

See [Isolating the Planes][isolating-planes] for further details.

[applications]: ../reference-guide/terms.md#application
[builder]: components.md#builder
[components]: components.md
[containers]: ../reference-guide/terms.md#container
[controller]: components.md#controller
[database]: components.md#database
[isolating-planes]: ../managing-deis/isolating-the-planes.md
[logger]: components.md#logger
[publisher]: components.md#publisher
[registry]: components.md#registry
[router]: components.md#router
[store]: components.md#store
