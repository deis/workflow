# Development Environment

This document is for developers who are interested in working directly on the Deis codebase. In this guide, we walk you through the process of setting up a development environment that is suitable for hacking on most Deis components.

We try to make it simple to hack on Deis components. However, there are necessarily several moving pieces and some setup required. We welcome any suggestions for automating or simplifying this process.

!!! note
    The Deis team is actively engaged in containerizing Go and Python based development environments tailored specifically for Deis development in order to minimize the setup required.  This work is ongoing.  Refer to the [deis/router][router] project for a working example of a fully containerized development environment.

If you're just getting into the Deis codebase, look for GitHub issues with the label [easy-fix][]. These are more straightforward or low-risk issues and are a great way to become more familiar with Deis.

## Prerequisites

In order to successfully compile and test Deis binaries and build Docker images of Deis components, the following are required:

- [git][git]
- Go 1.5 or later, with support for compiling to `linux/amd64`
- [glide][glide]
- [golint][golint]
- [shellcheck][shellcheck]
- [Docker][docker] (in a non-Linux environment, you will additionally want [Docker Machine][machine])

For [deis/controller][controller], in particular, you will also need:

- Python 2.7 or later (with `pip`)
- virtualenv (`sudo pip install virtualenv`)

In most cases, you should simply install according to the instructions. There are a few special cases, though. We cover these below.

### Configuring Go

If your local workstation does not support the `linux/amd64` target environment, you will have to install Go from source with cross-compile support for that environment. This is because some of the components are built on your local machine and then injected into a Docker container.

Homebrew users can just install with cross compiling support:

```
$ brew install go --with-cc-common
```

It is also straightforward to build Go from source:

```
$ sudo su
$ curl -sSL https://golang.org/dl/go1.5.src.tar.gz | tar -v -C /usr/local -xz
$ cd /usr/local/go/src
$ # compile Go for our default platform first, then add cross-compile support
$ ./make.bash --no-clean
$ GOOS=linux GOARCH=amd64 ./make.bash --no-clean
```

Once you can compile to `linux/amd64`, you should be able to compile Deis components as normal.

### Configuring Docker Machine (Mac)

Deis needs Docker for building images.  Docker utilizes a client/server architecture, and while the Docker client is available for Mac OS, the Docker server is dependent upon the Linux kernel.  Therefore, in order to use Docker on Mac OS, [Docker Machine][machine] is used to facilitate running the Docker server within a [VirtualBox][vbox] VM.

Install Docker Machine according to the normal installation instructions, then use it to create a new VM:

```
$ docker-machine create deis-docker \
    --driver=virtualbox \
    --virtualbox-disk-size=100000 \
    --engine-insecure-registry 10.0.0.0/8 \
    --engine-insecure-registry 172.16.0.0/12 \
    --engine-insecure-registry 192.168.0.0/16 \
    --engine-insecure-registry 100.64.0.0/10
```

This will create a new virtual machine named `deis-docker` that will take up as much as 100,000 MB of disk space. The images you build may be large, so allocating a big disk is a good idea.

Once the `deis-docker` machine exists, source its values into your environment so your docker client knows how to use the new machine. You may even choose to add this to your bash profile or similar.

```
$ eval "$(docker-machine env docker-deis)"
```

After following these steps, some Docker Machine users report a slight delay (30 - 60 seconds) before the Docker server is ready.

!!! note
    In subsequent steps, you may run a Docker registry within the `deis-docker` VM. Such a registry will not have a valid SSL certificate and will use HTTP instead of HTTPS. Such registries are implicitly untrusted by the Docker server (which is also running on the `deis-docker` VM).  In order for the Docker server to trust the insecure registry, `deis-docker` is explicitly created to trust all registries in the IP ranges that that are reserved for use by private networks.  The VM (and therefore the registry) will exist within such a range.  This will effectively permit Docker pulls and pushes to such a registry.

## Fork the Repository

Once the prerequisites have been met, we can begin to work with Deis components.

Begin at Github by forking whichever Deis project you would like to contribute to, then clone that fork locally.  Since Deis is predominantly written in Go, the best place to put it is under `$GOPATH/src/github.com/deis/`.

```
$ mkdir -p  $GOPATH/src/github.com/deis
$ cd $GOPATH/src/github.com/deis
$ git clone git@github.com:<username>/<component>.git
$ cd <component>
```

!!! note
    By checking out the forked copy into the namespace `github.com/deis/<component>`, we are tricking the Go toolchain into seeing our fork as the "official" source tree.

If you are going to be issuing pull requests to the upstream repository from which you forked, we suggest configuring Git such that you can easily rebase your code to the upstream repository's master branch. There are various strategies for doing this, but the [most common](https://help.github.com/articles/fork-a-repo/) is to add an `upstream` remote:

```
$ git remote add upstream https://github.com/deis/<component>.git
```

For the sake of simplicity, you may want to point an environment variable to your Deis code - the directory containing one or more Deis components:

```
$ export DEIS=$GOPATH/src/github.com/deis
```

Throughout the rest of this document, `$DEIS` refers to that location.

### Alternative: Forking with a Pushurl

A number of Deis contributors prefer to pull directly from `deis/<component>`, but push to `<username>/<component>`. If that workflow suits you better, you can set it up this way:

```
$ git clone git@github.com:deis/<component>.git
$ cd deis
$ git config remote.origin.pushurl git@github.com:<username>/<component>.git
```

In this setup, fetching and pulling code will work directly with the upstream repository, while pushing code will send changes to your fork. This makes it easy to stay up to date, but also make changes and then issue pull requests.

## Make Your Changes

With your development environment set up and the code you wish to work on forked and cloned, you can begin making your changes.

## Test Your Changes

Deis components each include a comprehensive suite of automated tests, mostly written in Go. See [testing][] for instructions on running the tests.

## Deploying Your Changes

Although writing and executing tests are critical to ensuring code quality, most contributors will also want to deploy their changes to a live environment, whether to make use of those changes or to test them further.  The remainder of this section documents the procedure for running officially released Deis components in a development cluster and replacing any one of those with your customizations.

### Running a Kubernetes Cluster for Development

To run a Kubernetes cluster locally or elsewhere to support your development activities, refer to Deis installation instructions [here](../quickstart/index.md).

### Using a Development Registry

To facilitate deploying Docker images containing your changes to your Kubernetes cluster, you will need to make use of a Docker registry.  This is a location to where you can push your custom-built images and from where your Kubernetes cluster can retrieve those same images.

If your development cluster runs locally (in Vagrant, for instance), the most efficient and economical means of achieving this is to run a Docker registry locally _as_ a Docker container.

To facilitate this, most Deis components provide a make target to create such a registry:

```
$ make dev-registry
```

In a Linux environment, to begin using the registry:

```
export DEIS_REGISTRY=<IP of the host machine>:5000
```

In non-Linux environments:

```
export DEIS_REGISTRY=<IP of the docker-deis Docker Machine VM>:5000/
```

If your development cluster runs on a cloud provider such as Google Container Engine, a local registry such as the one above will not be accessible to your Kubernetes nodes.  In such cases, a public registry such as [DockerHub][dh] or [quay.io][quay] will suffice.

To use DockerHub for this purpose, for instance:

```
$ export DEIS_REGISTRY=""
$ export IMAGE_PREFIX=<your DockerHub username>
```

To use quay.io:

```
$ export DEIS_REGISTRY=quay.io/
$ export IMAGE_PREFIX=<your quay.io username>
```

Note the importance of the trailing slash.

### Dev / Deployment Workflow

With a functioning Kubernetes cluster and the officially released Deis components installed onto it, deployment and further testing of any Deis component you have made changes to is facilitated by replacing the officially released component with a custom built image that contains your changes.  Most Deis components include Makefiles with targets specifically intended to facilitate this workflow with minimal friction.

In the general case, this workflow looks like this:

1. Update source code and commit your changes using `git`
2. Use `make build` to build a new Docker image
3. Use `make dev-release` to generate Kubernetes manifest(s)
4. Use `make deploy` to restart the component using the updated manifest

This can be shortened to a one-liner using just the `deploy` target:

```
$ make deploy
```

## Useful Commands

Once your customized Deis component has been deployed, here are some helpful commands that will allow you to inspect your cluster and to troubleshoot, if necessary:

### See All Deis Pods

```
$ kubectl --namespace=deis get pods
```

### Describe a Pod

This is often useful for troubleshooting pods that are in pending or crashed states:

```
$ kubectl --namespace=deis describe -f <pod name>
```

### Tail Logs

```
$ kubectl --namespace=deis logs -f <pod name>
```

### Django Shell

Specific to [deis/controller][controller]

```
$ kubectl --namespace=deis exec -it <pod name> -- python manage.py shell
```

Have commands other Deis contributors might find useful? Send us a PR!

## Pull Requests

Satisfied with your changes?  Share them!

Please read [Submitting a Pull Request](submitting-a-pull-request.md). It contains a checklist of
things you should do when proposing a change to any Deis component.

[router]: https://github.com/deis/router
[easy-fix]: https://github.com/issues?q=user%3Adeis+label%3Aeasy-fix+is%3Aopen
[git]: https://git-scm.com/
[glide]: https://github.com/Masterminds/glide
[golint]: https://github.com/golang/lint
[shellcheck]: https://github.com/koalaman/shellcheck
[docker]: https://www.docker.com/
[machine]: http://docs.docker.com/machine/install-machine/
[controller]: https://github.com/deis/controller
[vbox]: https://www.virtualbox.org/
[testing]: testing.md
[k8s]: http://kubernetes.io/
[k8s-getting-started]: http://kubernetes.io/gettingstarted/
[pr]: submitting-a-pull-request.md
[dh]: https://hub.docker.com/
[quay]: https://quay.io/
