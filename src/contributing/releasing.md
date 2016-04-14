# Releasing a new Deis version

This document describes how to release a new Deis version. It's targetted toward the Deis core
maintainers.

The below sections present a step by step guide to releasing a new Deis Workflow. Throughout all
examples, we'll be assuming we're going to release `$DEIS_RELEASE`. Before you begin, set this
environment variable to the correct version that you intend to release (for example, `2.0.0-beta2`).

# What's a release?

A release consists of the following artifacts:

1. Docker images with `$DEIS_RELEASE` tags for each Deis Workflow component:
  - [builder](https://github.com/deis/builder)
  - [controller](https://github.com/deis/controller)
  - [dockerbuilder](https://github.com/deis/dockerbuilder)
  - [fluentd](https://github.com/deis/fluentd)
  - [logger](https://github.com/deis/logger)
  - [minio](https://github.com/deis/minio)
  - [postgres](https://github.com/deis/postgres)
  - [registry](https://github.com/deis/registry)
  - [router](https://github.com/deis/router)
  - [slugbuilder](https://github.com/deis/slugbuilder)
  - [slugrunner](https://github.com/deis/slugrunner)
  - [workflow](https://github.com/deis/worflow)
  - [workflow-e2e](https://github.com/deis/workflow-e2e)
  - [workflow-manager](https://github.com/deis/workflow-manager) (v2.0.0-beta1-8-g9ba6db7)
2. A new [Helm chart for Deis](https://github.com/deis/charts) that references all of the new
images referenced above. For example, if `$DEIS_RELEASE` is `2.0.0-beta2`, the new chart would
be in a new directory called `workflow-beta2`.

# Step 1: Get the status of all components

First, we'll need to get the statuses of all repositories that house the components we're
interested in upgrading. We'll use
[sgoings/deis-workflow-group](https://github.com/sgoings/deis-workflow-group) to do that in one
place. That repository is a group of git submodules with all of the applicable repositories in it,
so that we can manage everything from one place.

Clone that repository to any location on your local machine, and make sure to update all submodules:

```console
git clone https://github.com/sgoings/deis-workflow-group
cd deis-workflow-group
make git-update
```

# Step 2: Create a new Helm chart

TODO

- Copy from old chart
- Run `git submodule update` to get git SHAs
- Update `generate_params.toml`
- Branch and PR your new chart (the branch should be called `release-$DEIS_RELEASE`)

# Step 3: Manual Testing

After the chart is created with the immutable Docker image tags that represent the final images
(i.e. the ones that will be re-tagged to the immutable release tag, such as `2.0.0-beta2`), it
should be manually tested by as many people as possible. Special attention should be paid to the
user experience, both from an operator and developer perspective.

Our goal is to test with as many object storage and Kubernetes installation configurations as
possible, to ensure there are no gaps in configuration or functionality. See below for a testing
matrix.

Object Storage / Kubernetes Install | Kube-Solo | Google Container Engine | AWS | Micro-Kube | Vagrant |
----------------------------------- | --------- | ----------------------- | --- | ---------- | ------- |
Default (Minio)                     |
Google Cloud Storage                |
Amazon S3                           |

# Step 4: Tag and push Docker images

TODO

Tag docker images for each component, from the Docker tags that you set in step 2 to ``$DEIS_RELEASE`

# Step 5: Update changelogs

TODO

Update changelogs for each repository

# Step 6: Tag and push git repos

Inside the deis-workflow-group directory, run:

```console
TAG=$DEIS_RELEASE TAG_MESSAGE="releasing workflow $DEIS_RELEASE" make git-tag
make git-tag-push
```
