# Release Checklist

This document describes how to release a new Workflow version. It's targeted toward the Deis core
maintainers.

The below sections present a step-by-step guide to publish a new Workflow release. Throughout all
of the examples, we'll be assuming that the below two environment variables are present in wherever
you're working. Make sure to set them (e.g. by `export`ing them) before you get started.

- `$WORKFLOW_RELEASE` - the full name of this version. For example, `v2.0.0-beta4`
- `$WORKFLOW_RELEASE_SHORT` - The short name of this version. For example, `beta4`

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
images referenced above. For example, if `$WORKFLOW_RELEASE` is `2.0.0-beta4`, the new chart would
be in a new directory called `workflow-beta4`.

# Step 1: Create New Helm Classic Charts

First, export necessary values for `WORKFLOW_RELEASE` and `WORKFLOW_RELEASE_SHORT`:
```
export WORKFLOW_RELEASE=<full release name>
export WORKFLOW_RELEASE_SHORT=<short form of above>
```

Next, we'll create new [Helm Classic](https://github.com/helm/helm-classic) charts so that we can "stage" a
version of our release for testing. Here is the current process to do so:

1. Create a new branch in [deis/charts](https://github.com/deis/charts): `git checkout -b release-$WORKFLOW_RELEASE origin/master`
2. Download the [deisrel](https://github.com/deis/deisrel) binary via the bintray link provided in the project's README and place it in your `$PATH`
3. Stage copies of all files needing release updates into the appropriate `workflow-$WORKFLOW_RELEASE_SHORT(-e2e)` chart directories.  (Note: `deisrel` will automatically fetch the latest commit sha values from the `master` branch of each repo to populate the appropriate component's `dockerTag` in `tpl/generate_params.toml`):
  ```
  deisrel helm-stage --stagingDir workflow-$WORKFLOW_RELEASE_SHORT workflow
  deisrel helm-stage --stagingDir workflow-$WORKFLOW_RELEASE_SHORT-e2e e2e
  ```
4. Delete the `KUBERNETES_POD_TERMINATION_GRACE_PERIOD_SECONDS` env var from `workflow-$WORKFLOW_RELEASE_SHORT/tpl/deis-controller-rc.yaml`
5. Commit your changes:
  ```
  git commit -a -m "chore(workflow-$WORKFLOW_RELEASE_SHORT): releasing workflow-$WORKFLOW_RELEASE_SHORT(-e2e)"
  ```
6. Push your changes: `git push origin HEAD:release-$WORKFLOW_RELEASE`.
7. Open a pull request from your branch to merge into `master` on https://github.com/deis/charts

# Step 2: Kick off Jenkins Job

Navigate to https://ci.deis.io/job/workflow-test-release/ and kick off a new job with appropriate build parameters filled out, i.e. `HELM_REMOTE_BRANCH=$WORKFLOW_RELEASE` and `RELEASE=$WORKFLOW_RELEASE_SHORT`

As of this writing, the e2e tests in this job are run on a GKE cluster using default (minio) external storage.

# Step 3: Manual Testing

After the chart is created with the immutable Docker image tags that represent the final images
(i.e. the ones that will be re-tagged to the immutable release tag, such as `2.0.0-beta4`), it
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
      - Push this change to the release branch

# Step 4: Tag and Push Docker Images

After everyone has tested and determined that there are no show-stopping problems for this release,
it's time to tag each individual Docker image with `$WORKFLOW_RELEASE`.

To do so, simply go back to the directory where you checked out the `deis-workflow-group` repo
and run the following two commands to tag and push updated docker images:

```console
make git-update
TAG=$WORKFLOW_RELEASE make docker-tag docker-push
```

# Step 5: Update Helm Classic Chart

Now that new Docker images are on public Docker repositories, it's time to update the Helm Classic chart
to reference the official images. We will use `deisrel` to do this.  The following will change every `dockerTag` value
to the same `$WORKFLOW_RELEASE` as well as now pointing to the `deis` quay org.

```
deisrel helm-params --stage --tag $WORKFLOW_RELEASE --org deis workflow
deisrel helm-params --stage --tag $WORKFLOW_RELEASE --org deis e2e
```

Copy the updated files back into charts:
```
cp -r staging/workflow-dev/* workflow-$WORKFLOW_RELEASE_SHORT
cp -r staging/workflow-dev-e2e/* workflow-$WORKFLOW_RELEASE_SHORT-e2e
```

Double-check that `workflow-dev/tpl/generate_params.toml`, has the value `https://versions.deis.com` for `versionsApiURL` entry under `workflowManager`.

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
deisrel changelog individual $REPO_NAME $PREVIOUS_TAG $CURRENT_SHA $WORKFLOW_RELEASE
```

This command will output the new changelog entry to STDOUT. Copy it and prepend it to the existing `CHANGELOG.md` file.

Finally, commit, push and submit a pull request for your changes:

```console
git commit CHANGELOG.md -m "doc(CHANGELOG.md): add entry for $WORKFLOW_RELEASE"
git push -u $YOUR_FORK_REMOTE release-$WORKFLOW_RELEASE_SHORT
```

Before you continue, ensure pull requests in all applicable repositories are reviewed, and merge them.

# Step 7: Tag and Push Git Repositories

The final step of the release process is to tag each git repository, and push the tag to each
GitHub project. To do so, simply run the below command in the `deisrel` repository:

```console
deisrel git tag $WORKFLOW_RELEASE
```

# Step 8: Close GitHub Milestones

Close the github milestone by creating a new pull request at
[seed-repo](https://github.com/deis/seed-repo). Any changes merged to master on that repository
will be applied to all of the component projects. If there are open issues attached to the
milestone, move them to the next upcoming milestone before merging the pull request.

# Step 9: Let Everyone Know

Jump in #company on slack and let folks know that the release has been cut! This will let
folks in supporting functions know that they should start the release support process including
summary blog posts, tweets, notes for the monthly newsletter updates, etc.

Provide a gist to the aggregated release notes.  We can generate the aggregated changelog data from `deisrel`:

```console
deisrel changelog global $PREVIOUS_TAG $WORKFLOW_RELEASE
```

You are now done with the release.
