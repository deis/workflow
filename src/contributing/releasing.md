# Releasing a new Deis version

This document describes how to release a new Deis version. It's targetted toward the Deis core
maintainers.

The below sections present a step by step guide to releasing a new Deis Workflow. Throughout all
examples, we'll be assuming that the below two environment variables are present in wherever
you're working. Make sure to set them (e.g. by `export`ing them) before you get started.

- `$DEIS_RELEASE` - the full name of this version. For example, `v2.0.0-beta2`
- `$DEIS_RELEASE_SHORT` - The short name of this version. For example, `beta2`

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

Clone that repository to any location on your local machine, update all submodules and list
the latest commit for each submodule:

```console
git clone https://github.com/sgoings/deis-workflow-group
cd deis-workflow-group
make git-update
git submodule status
```

Keep the list of commit SHAs handy - you'll need it for later.

# Step 2: Create a new Helm chart

Next, we'll create a new [Helm](https://github.com/helm/helm) chart so that we can "stage" a
version of our release for testing. The process is fairly simple:

1. Create a new branch: `git checkout -b release-$DEIS_RELEASE`
2. Copy an existing chart: `cp -r workflow-beta2 workflow-$DEIS_RELEASE_SHORT`
3. Modify the `workflow-$DEIS_RELEASE_SHORT/tpl/generate_params.toml` file to ensure that all
`dockerTag` values look like `git-$COMPONENT_SHA_SHORT`, where `$COMPONENT_SHA_SHORT` is the first
7 characters of the applicable SHA that you got in the previous step.
4. Commit your changes: `git commit -a -m "chore(workflow-$DEIS_RELEASE_SHORT): releasing workflow-$DEIS_RELEASE_SHORT"`
5. Push your changes to your fork: `git push -u $YOUR_FORK_REMOTE release-$DEIS_RELEASE`. Note that
`$YOUR_FORK_REMOTE` is the git URI to the remote of your `deis/charts` fork. Mine is `git@github.com:arschles/deis-charts.git`, for example.
6. Open a pull request from your branch to merge into `master` on https://github.com/deis/charts

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

After everyone has tested and determined that there are no showstopping problems for this release,
it's time to tag each individual Docker image with `$DEIS_RELEASE`.

TODO

# Step 5: Update Changelogs

TODO

Update changelogs for each repository

# Step 6: Tag and push git repos

Inside the deis-workflow-group directory, run:

```console
TAG=$DEIS_RELEASE TAG_MESSAGE="releasing workflow $DEIS_RELEASE" make git-tag
make git-tag-push
```
