# Architecture

Deis uses a service oriented architecture with [components][]
grouped into a Control Plane, Data Plane and Router Mesh.

## System Diagram

![Deis System Diagram](DeisSystemDiagram.png)

Operators use [Helm][] to stand up the cluster's Control Plane, Data Plane and Router Mesh.
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

End-users interact primarily with the [controller][] which exposes an
HTTP API. They can also interact with the [builder][] via `git push`.

## Data Plane

![Deis Data Plane Architecture](DeisDataPlane.png)

The Data Plane is where [containers][] (in blue) are run on behalf of end-users.

The platform scheduler is in charge of placing containers on hosts in the data plane.

## Router Mesh

![Deis Router Mesh Architecture](DeisRouterMesh.png)

The Router Mesh publishes [Applications][] to consumers.

Each [router][] in the mesh is a dynamically configured Nginx web server designed to route inbound
traffic to the appropriate Kubernetes services for applications running in the data and control
planes.  Additionally, routers perform typical web server responsibilities such as SSL termination
and gzip compression.

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
[helm]: http://helm.sh
[containers]: ../reference-guide/terms.md#container
[controller]: components.md#controller
[database]: components.md#database
[isolating-planes]: ../managing-deis/isolating-the-planes.md
[registry]: components.md#registry
[router]: components.md#router
[store]: components.md#store
