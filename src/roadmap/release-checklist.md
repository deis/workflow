# Release Checklist

This document describes how to release a new Workflow version. It's targeted toward the Deis core
maintainers.

The below sections present a step-by-step guide to publish a new Workflow release. Throughout all
of the examples, we'll be assuming that the below four environment variables are present wherever
you're working. Make sure to set them (e.g. by `export`ing them) before you get started.

- `$WORKFLOW_RELEASE` - the full name of this version. For example, `v2.0.0-rc2` for a pre-release version or `v2.0.0` otherwise.
- `$WORKFLOW_RELEASE_SHORT` - The short name of this version. For example, `rc2` for a pre-release version or identical to `$WORKFLOW_RELEASE` above otherwise.
- `$WORKFLOW_PREV_RELEASE` - the full name of the previous version. For example, `v2.0.0-rc1` for a pre-release version or `v2.0.0` otherwise.
- `$WORKFLOW_PREV_RELEASE_SHORT` - The short name of the previous version. For example, `rc1` for a pre-release version or identical to `$WORKFLOW_PREV_RELEASE` above otherwise.

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
images referenced above. For example, if `$WORKFLOW_RELEASE` is `2.0.0-v2.0.0`, the new chart would
be in a new directory called `workflow-v2.0.0`.

# Step 1: Cut repo branches and push image tags

  Once the release milestone is cleared of tickets in the workflow component repos, the release branches can be cut.

  If only a particular repo is ready, navigate to said repo and:

        git checkout master && git pull upstream master
        git checkout -b release-$WORKFLOW_RELEASE && git push upstream release-$WORKFLOW_RELEASE

  Otherwise, for bulk-cutting all repos at the same time, we will use [sgoings/deis-workflow-group](https://github.com/sgoings/deis-workflow-group) here and in Step 2 below:

        git clone git@github.com:sgoings/deis-workflow-group.git
        cd deis-workflow-group

        make git-update # point all repos to latest master commits
        BRANCH="release-${WORKFLOW_RELEASE}" NEW="true" make git-checkout-branch
        BRANCH="release-${WORKFLOW_RELEASE}" make git-push-branch #(can use DRY_RUN=true)

# Step 2: Create New Helm Classic Charts

Next, we'll create new [Helm Classic](https://github.com/helm/helm-classic) charts so that we can "stage" a
version of our release for testing. Here is the current process to do so:

  1. Checkout the `release-$WORKFLOW_RELEASE` branch in [deis/charts](https://github.com/deis/charts) (created in Step 1.1 above):

        git fetch upstream
        git checkout release-$WORKFLOW_RELEASE

  2. Download the [deisrel](https://github.com/deis/deisrel) binary via the links provided in the project's README. Once downloaded, place the binary in your `$PATH`.

  3. Copy the current `dev` charts into new `workflow-$WORKFLOW_RELEASE_SHORT` charts:

        cp -r workflow-dev workflow-$WORKFLOW_RELEASE_SHORT
        cp -r workflow-dev-e2e workflow-$WORKFLOW_RELEASE_SHORT-e2e
        cp -r router-dev router-$WORKFLOW_RELEASE_SHORT

  4. Stage copies of all files needing release updates into the appropriate chart directories created above, supplying `--ref release-$WORKFLOW_RELEASE` to specify this branch/ref for lookup of latest commit shas (informing `generate_params.toml`), as well as `--stagingDir <appropriate staging dir>` to inform `deisrel` where to put updated files:

        deisrel helm-stage --ref release-$WORKFLOW_RELEASE --stagingDir workflow-$WORKFLOW_RELEASE_SHORT workflow
        deisrel helm-stage --ref release-$WORKFLOW_RELEASE --stagingDir workflow-$WORKFLOW_RELEASE_SHORT-e2e e2e
        deisrel helm-stage --ref release-$WORKFLOW_RELEASE --stagingDir router-$WORKFLOW_RELEASE_SHORT router

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
`$WORKFLOW_RELEASE`. Use `git grep $WORKFLOW_PREV_RELEASE` and `git grep
$WORKFLOW_PREV_RELEASE_SHORT` to find any references. (Be careful not to change `CHANGELOG.md`)

Also, note there may be occurrences of an older release (prior to
`$WORKFLOW_PREV_RELEASE`) in `upgrading-workflow.md`. These should be changed to
`$WORKFLOW_PREV_RELEASE`.

# Step 5: Manual Testing

After the chart is created with the immutable Docker image tags that represent the final images
(i.e. the ones that will be re-tagged to the immutable release tag, such as `2.0.0-v2.0.0`), it
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
    - update the appropriate component's `dockerTag` value in the release chart with the `git-<issue_fix_sha>` from the cherry-pick commit above.
    - push updated chart change(s) to existing release branch and re-convene testing

When testing shows no further issues and the release chart is ready to ship, make sure the pull request is reviewed once more and merged before continuing.

!!! note

    If non-release-specific amendments have been made to the release chart that do
    not exist in the `workflow-dev`, be sure to PR said changes for this chart as well.

# Step 6: Tag and Push Docker Images

It's time to retag each individual Docker image with the 'official' `$WORKFLOW_RELEASE` value in the `deis` [quay.io](https://quay.io/organization/deis) org.

To do so, simply run the following `deisrel` command:

```console
deisrel docker retag $WORKFLOW_RELEASE --new-org="deis -ref release-$WORKFLOW_RELEASE"
```

# Step 7: Update Changelogs

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

# Step 8: Tag and Push Git Repositories

The final step of the release process is to tag each git repository, and push the tag to each
GitHub project. To do so, simply run the below command in the `deisrel` repository:

```console
deisrel git tag --ref release-$WORKFLOW_RELEASE $WORKFLOW_RELEASE
```

# Step 9: Close GitHub Milestones

Close the github milestone by creating a new pull request at
[seed-repo](https://github.com/deis/seed-repo). Any changes merged to master on that repository
will be applied to all of the component projects. If there are open issues attached to the
milestone, move them to the next upcoming milestone before merging the pull request.

# Step 10: Let Everyone Know

Jump in #company on slack and let folks know that the release has been cut! This will let
folks in supporting functions know that they should start the release support process including
summary blog posts, tweets, notes for the monthly newsletter updates, etc.

Provide a gist to the aggregated release notes.  We can generate the aggregated changelog data from `deisrel`:

```console
deisrel changelog global $PREVIOUS_TAG $WORKFLOW_RELEASE
```

You are now done with the release.
