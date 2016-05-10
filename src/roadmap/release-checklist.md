# Release Checklist

This document describes how to release a new Workflow version. It's targeted toward the Deis core
maintainers.

The below sections present a step-by-step guide to publish a new Workflow release. Throughout all
of the examples, we'll be assuming that the below two environment variables are present in wherever
you're working. Make sure to set them (e.g. by `export`ing them) before you get started.

- `$WORKFLOW_RELEASE` - the full name of this version. For example, `v2.0.0-beta3`
- `$WORKFLOW_RELEASE_SHORT` - The short name of this version. For example, `beta3`

# What's a Release?

A release consists of the following artifacts:

1. Docker images with `$WORKFLOW_RELEASE` tags for each Deis Workflow component:
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
  - [workflow](https://github.com/deis/workflow)
  - [workflow-e2e](https://github.com/deis/workflow-e2e)
  - [workflow-manager](https://github.com/deis/workflow-manager)
  - [workflow-cli](https://github.com/deis/workflow-cli)
2. A new [Helm Classic chart for Workflow](https://github.com/deis/charts) that references all of the new
images referenced above. For example, if `$WORKFLOW_RELEASE` is `2.0.0-beta3`, the new chart would
be in a new directory called `workflow-beta3`.

# Step 1: Get the Status of all Components

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

# Step 2: Create a New Helm Classic Chart

Next, we'll create a new [Helm Classic](https://github.com/helm/helm-classic) chart so that we can "stage" a
version of our release for testing. The process is fairly simple:

1. Create a new branch: `git checkout -b release-$WORKFLOW_RELEASE`
2. Copy the existing `dev` chart: `cp -r workflow-dev workflow-$WORKFLOW_RELEASE_SHORT`
3. Modify the `workflow-$WORKFLOW_RELEASE_SHORT/tpl/generate_params.toml` file to ensure that all
`dockerTag` values look like `git-$COMPONENT_SHA_SHORT`, where `$COMPONENT_SHA_SHORT` is the first
7 characters of the applicable SHA that you got in the previous step.
4. Ensure that all `DEBUG` variables in manifests are `false`.
5. Delete the `KUBERNETES_POD_TERMINATION_GRACE_PERIOD_SECONDS` env var from `tpl/deis-controller-rc.yaml`
6. Commit your changes: `git commit -a -m "chore(workflow-$WORKFLOW_RELEASE_SHORT): releasing workflow-$WORKFLOW_RELEASE_SHORT"`
7. Push your changes to your fork: `git push -u $YOUR_FORK_REMOTE release-$DEIS_RELEASE`. Note that
`$YOUR_FORK_REMOTE` is the git URI to the remote of your `deis/charts` fork. Mine is `git@github.com:arschles/deis-charts.git`, for example.
8. Do steps 2-5 with the `workflow-beta3-e2e` directory
9. Open a pull request from your branch to merge into `master` on https://github.com/deis/charts

# Step 3: Manual Testing

After the chart is created with the immutable Docker image tags that represent the final images
(i.e. the ones that will be re-tagged to the immutable release tag, such as `2.0.0-beta3`), it
should be manually tested by as many people as possible. Special attention should be paid to the
user experience, both from an operator and developer perspective.

Our goal is to test with as many object storage and Kubernetes installation configurations as
possible, to ensure there are no gaps in configuration or functionality. See below for a sample testing
matrix.

Object Storage / Kubernetes Install | Kube-Solo | Google Container Engine | AWS | Micro-Kube | Vagrant |
----------------------------------- | --------- | ----------------------- | --- | ---------- | ------- |
Default (Minio)                     |
Google Cloud Storage                |
Amazon S3                           |


!!! note
    If bugs are found and fixes are made, do the following:

      - Update the appropriate docker tag(s) in the `generate_params.toml` file
      - Run `make git-update` in the aforementioned `deis-workflow-group` repository

# Step 4: Tag and Push Docker Images

After everyone has tested and determined that there are no show-stopping problems for this release,
it's time to tag each individual Docker image with `$WORKFLOW_RELEASE`.

To do so, simply go back to the directory where you checked out the `deis-workflow-group` repo
and run the following two commands to tag and push updated docker images:

```console
TAG=$WORKFLOW_RELEASE make docker-tag docker-push
```

# Step 5: Update Helm Classic Chart

Now that new Docker images are on public Docker repositories, it's time to update the Helm Classic chart
to reference the official images. To do so, simply modify all `dockerTag` entries in the
`generate_params.toml` files in the `workflow-$WORKFLOW_RELEASE_SHORT` and
`workflow-$WORKFLOW_RELEASE_SHORT-e2e` to be `$WORKFLOW_RELEASE` (instead of the ones based on git tags).

Additionally, we want the official release chart to reference the production `versions.deis.com` API. Also in `generate_params.toml`, modify the `versionsApiURL` entry under `workflowManager` to have the value `https://versions.deis.com`.

Also, ensure that the `README.md` and `Chart.yaml` files in the new helm classic chart have updated references to the chart. For example, references to `helmc install workflow-betaX` should become `helmc install workflow-$WORKFLOW_RELEASE_SHORT`

If you find any references that should be bumped, open a pull-request against the documentation.

When you're done, commit and push your changes. You should get your pull request reviewed and merged before continuing.

**Note:** If non-release-specific amendments have been made to the release chart that do not exist in the `workflow-dev`, be sure to PR said changes for this chart as well.

# Step 6: Update Changelogs

At this point, part of the first part and all of the second part of the release is complete.
That is, the Helm Classic chart for the new Workflow version is done, and new Docker versions for all
components are done.

The remaining work is simply generating changelogs and tagging each component's GitHub repository.

First, create a branch for the new changelog:

```console
git checkout -b release-$WORKFLOW_RELEASE_SHORT
```

To generate changelogs, run the below command in each repository. Ensure that `$PREVIOUS_TAG` is
the previous tag that was generated in the repository.

```console
_scripts/generate_changelog.sh $PREVIOUS_TAG
```

This command will output the new changelog entry to STDOUT. Copy it and prepend it to the
existing `CHANGELOG.md` file, and make sure to change `HEAD` in the header of the entry
to `$WORKFLOW_RELEASE`.

Also copy the component changelog to a global release changelog, organized by component.
This will only live on your local machine while doing the release. Once changelogs for all
the components have been collected, publish the combined release notes as a gist so folks
in Step 9 can start preparing supporting content for the release.

Finally, commit, push and submit a pull request for your changes:

```console
git commit CHANGELOG.md -m "doc(CHANGELOG.md): add entry for $WORKFLOW_RELEASE_SHORT"
git push -u $YOUR_FORK_REMOTE $WORKFLOW_RELEASE_SHORT
```

Before you continue, ensure pull requests in all applicable repositories are reviewed, and merge
them.

# Step 7: Tag and Push Git Repositories

The final step of the release process is to tag each git repository, and push the tag to each
GitHub project. To do so, simply run the below command in the `deis-workflow-group` repository:

```console
TAG=$WORKFLOW_RELEASE TAG_MESSAGE="releasing workflow $WORKFLOW_RELEASE" make git-tag git-tag-push
```

# Step 8: Close GitHub Milestones

For each of the component projects listed at the top of this document, as well as for
[workflow-cli](https://github.com/deis/workflow-cli), visit its GitHub repository and close
the appropriate milestone. If there are still open issues attached to it, move them to
the next upcoming milestone before closing.

# Step 9: Let Everyone Know

Jump in #company on slack and let folks know that the release has been cut! This will let
folks in supporting functions know that they should start the release support process including
summary blog posts, tweets, notes for the monthly newsletter updates, etc. Providing a
gist to the aggregated release notes would be super-fly.

You are now done with the release.
