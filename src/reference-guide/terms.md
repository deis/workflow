# Terms


## Application

An application services requests and background jobs for a deployed git repository. Each application includes a set of Containers used to run isolated processes, and a Release that defines the current Build and Config deployed by containers.


## Build

Deis builds are created automatically on the controller when a developer uses `git push deis master`. When a new build is created, a new Release is created automatically.


# Config

Config refers to a set of environment variables used by Containers in as Application.

When Config is changed, a new Release is created automatically.


## Container

Deis containers are instances of Docker containers used to run Applications. Containers perform the actual work of an Application by servicing requests or by running background tasks as part of the cluster.


### Ephemeral Filesystem

Each container gets its own ephemeral filesystem, with a fresh copy of the most recently deployed code. During the container’s lifetime, its running processes can use the filesystem as a temporary scratchpad, but no files that are written are visible to processes in any other container. Any files written to the ephemeral filesystem will be discarded the moment the container is either stopped or restarted.


### Container States

There are several states that a container can be in at any time. The states are:

- initialized - the state of the container before it is created
- created - the container is built and ready for operation
- up - the container is running
- down - the container crashed or is stopped
- destroyed - the container has been destroyed


## Controller

The controller is the "brain" of the Deis platform. A controller manages Applications and their lifecycle.

The controller is in charge of:

- Authenticating and authorizing clients
- Processing client API calls
- Managing containers that perform work for applications
- Managing proxies that route traffic to containers
- Managing users, keys and other base configuration

The Controller stack includes:

- Django API Server for handling API calls


## Key

Deis keys are SSH Keys used during the git push process. Each user can use the client to manage a list of keys on the Controller.


## Release

A Deis release is a combination of a Build with a Config. Each Application is associated with one release at a time. Deis releases are numbered and new releases always increment by one (e.g. v1, v2, v3).

Containers that host an application use these release versions to pull the correct code and configuration.


## Scheduler

The Scheduler is responsible for creating, starting, stopping, and destroying Containers. For example, a command such as `deis scale cmd=10` tells the Scheduler to run ten Containers from the Docker image for your Application.

The Scheduler must decide which machines are eligible to run these container jobs. Scheduler backends vary in the details of their job allocation policies and whether or not they are resource-aware, among other features.

The Deis scheduler client is implemented in the Controller component.


## Service

A Kubernetes Service is an abstraction which defines a logical set of Pods and a policy by which to access them. In Workflow, a Service is used to load-balance an application's [Containers](#containers) internally through a virtual IP address.
