# Release Checklist

This document describes how to release a new Workflow version. It's targeted toward the Deis core
maintainers.

The below sections present a step-by-step guide to publish a new Workflow release. Throughout all
of the examples, we'll be assuming that the below two environment variables are present in wherever
you're working. Make sure to set them (e.g. by `export`ing them) before you get started.

- `$WORKFLOW_RELEASE` - the full name of this version. For example, `v2.0.0-rc2`
- `$WORKFLOW_RELEASE_SHORT` - The short name of this version. For example, `rc2`

# What's a Release?

A release consists of the following artifacts:

1. Docker images with `$WORKFLOW_RELEASE` tags for each Deis Workflow component:
  - [builder](https://github.com/deis/builder)
  - [controller](https://github.com/deis/controller)
  - [dockerbuilder](https://github.com/deis/dockerbuilder)
  - [fluentd](https://github.com/deis/fluentd)
  - [logger](https://github.com/deis/logger)
  - [minio](https://github.com/deis/minio)
  - [monitor](https://github.com/deis/monitor)
  - [postgres](https://github.com/deis/postgres)
  - [registry](https://github.com/deis/registry)
  - [router](https://github.com/deis/router)
  - [slugbuilder](https://github.com/deis/slugbuilder)
  - [slugrunner](https://github.com/deis/slugrunner)
  - [stdout-metrics](https://github.com/deis/stdout-metrics)
  - [workflow](https://github.com/deis/workflow)
  - [workflow-e2e](https://github.com/deis/workflow-e2e)
  - [workflow-manager](https://github.com/deis/workflow-manager)
  - [workflow-cli](https://github.com/deis/workflow-cli)
2. A new [Helm Classic chart for Workflow](https://github.com/deis/charts) that references all of the new
images referenced above. For example, if `$WORKFLOW_RELEASE` is `2.0.0-rc2`, the new chart would
be in a new directory called `workflow-rc2`.

# Step 1: Cut repo branches and push image tags

  1. Once the release milestone is cleared of tickets in the workflow component repos, the release branches can be cut.  

    If only a particular repo is ready, navigate to said repo and:

          git checkout master && git pull upstream master
          git checkout -b release-$WORKFLOW_RELEASE && git push upstream release-$WORKFLOW_RELEASE

    Otherwise, for bulk-cutting all repos at the same time, we will use [sgoings/deis-workflow-group](https://github.com/sgoings/deis-workflow-group) here and in Step 2 below:

          git clone git@github.com:sgoings/deis-workflow-group.git
          cd deis-workflow-group

          make git-update # point all repos to latest master commits
          BRANCH="release-${WORKFLOW_RELEASE}" NEW="true" make git-checkout-branch
          BRANCH="release-${WORKFLOW_RELEASE}" make git-push-branch #(can use DRY_RUN=true)

  2. Tag and push docker images to 'staging' `deisci` org

          TAG="${WORKFLOW_RELEASE}" ORG="deisci" make docker-tag docker-push #(can use DRY_RUN=true)

# Step 2: Create New Helm Classic Charts

Next, we'll create new [Helm Classic](https://github.com/helm/helm-classic) charts so that we can "stage" a
version of our release for testing. Here is the current process to do so:

  1. Create a new branch in [deis/charts](https://github.com/deis/charts):

        git checkout -b release-$WORKFLOW_RELEASE upstream/master

  2. Download the [deisrel](https://github.com/deis/deisrel) binary via the links provided in the project's README. Once downloaded, place the binary in your `$PATH`.

  3. Copy the current `dev` charts into new `workflow-$WORKFLOW_RELEASE_SHORT` charts:

        cp -r workflow-dev workflow-$WORKFLOW_RELEASE_SHORT
        cp -r workflow-dev-e2e workflow-$WORKFLOW_RELEASE_SHORT-e2e
        cp -r router-dev router-$WORKFLOW_RELEASE_SHORT

  4. Stage copies of all files needing release updates into the appropriate `workflow-$WORKFLOW_RELEASE_SHORT(-e2e)` chart directories:

        deisrel helm-stage --tag $WORKFLOW_RELEASE --stagingDir workflow-$WORKFLOW_RELEASE_SHORT workflow
        deisrel helm-stage --tag $WORKFLOW_RELEASE --stagingDir workflow-$WORKFLOW_RELEASE_SHORT-e2e e2e
        deisrel helm-stage --tag $WORKFLOW_RELEASE --stagingDir router-$WORKFLOW_RELEASE_SHORT router

  5. Delete the `KUBERNETES_POD_TERMINATION_GRACE_PERIOD_SECONDS` env var from `workflow-$WORKFLOW_RELEASE_SHORT/tpl/deis-controller-rc.yaml`

  6. Test the new Workflow chart and make sure it installs:

        cp -r workflow-$WORKFLOW_RELEASE_SHORT* `helmc home`/workspace/charts
        helmc generate workflow-$WORKFLOW_RELEASE_SHORT
        helmc install workflow-$WORKFLOW_RELEASE_SHORT

    Optionally, run the e2e tests as well:

        helmc generate workflow-$WORKFLOW_RELEASE_SHORT-e2e
        helmc install workflow-$WORKFLOW_RELEASE_SHORT-e2e

  7. Commit your changes:

        git commit -a -m "chore(workflow-$WORKFLOW_RELEASE_SHORT): releasing workflow-$WORKFLOW_RELEASE_SHORT(-e2e)"

  8. Push your changes:

        git push upstream HEAD:release-$WORKFLOW_RELEASE


  9. Open a pull request from your branch to merge into `master` on https://github.com/deis/charts

# Step 3: Kick off Jenkins Jobs

Navigate to https://ci.deis.io/job/workflow-test-release/ and kick off a new job with appropriate build parameters filled out, i.e. `HELM_REMOTE_BRANCH=$WORKFLOW_RELEASE` and `RELEASE=$WORKFLOW_RELEASE_SHORT`

As of this writing, the e2e tests in this job are run on a GKE cluster using default (minio) storage. To kick off the supported external storage permutations, run https://ci.deis.io/job/storage_backend_e2e/ w/ `STORAGE_TYPE` of 'gcs' and 'aws', along with the other
values used in job above.

# Step 4: Update Documentation

Create a new pull request against deis/workflow, updating all references of the old release to
`$WORKFLOW_RELEASE`. Use `git grep $WORKFLOW_OLD_RELEASE` to find any references. (Be careful not to
  change `CHANGELOG.md`)

Also, note there may be an occurrence of the previous oldest release (prior to `$WORKFLOW_OLD_RELEASE`) in
`upgrading-workflow.md`.  This should be changed to `$WORKFLOW_OLD_RELEASE`.

# Step 5: Manual Testing

After the chart is created with the immutable Docker image tags that represent the final images
(i.e. the ones that will be re-tagged to the immutable release tag, such as `2.0.0-rc2`), it
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

    - PR the fix, get it reviewed and merged into master of component repo(s)
    - git cherry-pick <issue_fix_sha> into the `release-$WORKFLOW_RELEASE` branch(es) of component repo(s)
    - retag the `git-<issue_fix_sha>` image with `$WORKFLOW_RELEASE` and push to 'staging' `deisci` quay org.

# Step 6: Tag and Push Docker Images

After everyone has tested and determined that there are no show-stopping problems for this release,
it's time to tag each individual Docker image with `$WORKFLOW_RELEASE`.

To do so, simply go back to the directory where you checked out the `deis-workflow-group` repo
and run the following two commands to tag and push updated docker images to the 'prod' `deis` quay org:

```console
BRANCH="release-$WORKFLOW_RELEASE" make git-checkout-branch
TAG=$WORKFLOW_RELEASE ORG="deis" make docker-tag docker-push
```

# Step 7: Update Helm Classic Chart

Now that new Docker images are on public Docker repositories, it's time to update the Helm Classic chart
to reference the official images. We will use `deisrel` to do this.  The following will change every `dockerTag` value
to the same `$WORKFLOW_RELEASE` as well as now pointing to the `deis` quay org.

```console
cd <back_to_charts_dir>
deisrel helm-stage --tag $WORKFLOW_RELEASE --stagingDir workflow-$WORKFLOW_RELEASE_SHORT --org deis workflow
deisrel helm-stage --tag $WORKFLOW_RELEASE --stagingDir workflow-$WORKFLOW_RELEASE_SHORT-e2e --org deis e2e
deisrel helm-stage --tag $WORKFLOW_RELEASE --stagingDir router-$WORKFLOW_RELEASE_SHORT --org deis router
```

When you're done, commit and push your changes. You should get your pull request reviewed and merged before continuing.

!!! note

    If non-release-specific amendments have been made to the release chart that do
    not exist in the `workflow-dev`, be sure to PR said changes for this chart as well.

# Step 8: Update Changelogs

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

# Step 9: Tag and Push Git Repositories

The final step of the release process is to tag each git repository, and push the tag to each
GitHub project. To do so, simply run the below command in the `deisrel` repository:

```console
deisrel git tag --ref release-$WORKFLOW_RELEASE $WORKFLOW_RELEASE
```

# Step 10: Close GitHub Milestones

Close the github milestone by creating a new pull request at
[seed-repo](https://github.com/deis/seed-repo). Any changes merged to master on that repository
will be applied to all of the component projects. If there are open issues attached to the
milestone, move them to the next upcoming milestone before merging the pull request.

# Step 11: Let Everyone Know

Jump in #company on slack and let folks know that the release has been cut! This will let
folks in supporting functions know that they should start the release support process including
summary blog posts, tweets, notes for the monthly newsletter updates, etc.

Provide a gist to the aggregated release notes.  We can generate the aggregated changelog data from `deisrel`:

```console
deisrel changelog global $PREVIOUS_TAG $WORKFLOW_RELEASE
```

You are now done with the release.
