# Releases

Deis uses a [continuous delivery][] approach for creating releases. Every merged commit that passes
testing results in a deliverable that can be given a [semantic version][] tag and shipped.

The master `git` branch of a project should always work. Only changes considered ready to be
released publicly are merged.


## Components Release as Needed

Deis components release new versions as often as needed. Fixing a high priority bug requires the
project maintainer to create a new patch release. Merging a backward-compatible feature implies
a minor release.

By releasing often, each component release becomes a safe and routine event. This makes it faster
and easier for users to obtain specific fixes. Continuous delivery also reduces the work
necessary to release a product such as Deis Workflow, which integrates several components.

"Components" applies not just to Deis Workflow projects, but also to development and release
tools, to Docker base images, and to other Deis projects that do [semantic version][] releases.

See "[How to Release a Component](#how-to-release-a-component)" for more detail.


## Workflow Releases Each Month

Deis Workflow has a regular, public release cadence. From v2.8.0 onward, new Workflow feature
releases arrive on the first Thursday of each month. Patch releases are created at any time,
as needed. GitHub milestones are used to communicate the content and timing of major and minor
releases, and longer-term planning is visible at [the Roadmap](roadmap.md).

Workflow release timing is not linked to specific features. If a feature is merged before the
release date, it is included in the next release.

See "[How to Release Workflow](#how-to-release-workflow)" for more detail.


## Semantic Versioning

Deis releases comply with [semantic versioning][semantic version], with the "public API" broadly
defined as:

- REST, gRPC, or other API that is network-accessible
- Library or framework API intended for public use
- "Pluggable" socket-level protocols users can redirect
- CLI commands and output formats

In general, changes to anything a user might reasonably link to, customize, or integrate with
should be backward-compatible, or else require a major release. Deis users can be confident that
upgrading to a patch or to a minor release will not break anything.


## How to Release a Component

Most Deis projects are "components" which produce a Docker image or binary executable as a
deliverable. This section leads a maintainer through creating a component release.

### Step 1: Update Code and Run the Release Tool

Major or minor releases should happen on the master branch. Patch releases
should check out the previous release tag and cherry-pick specific commits from master.

**Note:** if a patch release, the release artifact will have to be manually promoted by triggering
the [component-promote](https://ci.deis.io/job/component-promote) job with the following values:

```bash
COMPONENT_NAME=<component name>
COMPONENT_SHA=<patch commit sha>
```

Make sure you have the [deisrel][] release tool in your search `$PATH`.

Run `deisrel release` once with a fake semver tag to proofread the changelog content. (If `HEAD`
of master is not what is intended for the release, add the `--sha` flag as described
in `deisrel release --help`.)

```bash
$ deisrel release controller v0.0.0
Doing a dry run of the component release...
skipping commit 943a49267eeb28546819a266654806cfcbae0e38

Creating changelog for controller with tag v2.8.1 through commit 943a49267eeb28546819a266654806cfcbae0e38

### v2.8.1 -> v0.0.0

#### Fixes

- [`615b834`](https://github.com/deis/controller/commit/615b834f39cb68a854cc1f1e2f0f82d862ea2731) boot: Ensure DEIS_DEBUG==true for debug output
```

Based on the changelog content, determine whether the component deserves a minor or patch
release. Run the command again with that semver tag and `--dry-run=false`. You will still be
asked for confirmation before the release is created:
```bash
$ deisrel release controller v2.8.2 --dry-run=false
skipping commit 943a49267eeb28546819a266654806cfcbae0e38

Creating changelog for controller with tag v2.8.1 through commit 943a49267eeb28546819a266654806cfcbae0e38

### v2.8.1 -> v2.8.2


#### Fixes

- [`615b834`](https://github.com/deis/controller/commit/615b834f39cb68a854cc1f1e2f0f82d862ea2731) boot: Ensure DEIS_DEBUG==true for debug output


Please review the above changelog contents and ensure:
  1. All intended commits are mentioned
  2. The changes agree with the semver release tag (major, minor, or patch)

Create release for Deis Controller v2.8.2? [y/n]: y
New release is available at https://github.com/deis/controller/releases/tag/v2.8.2
```

### Step 2: Verify the Component is Available

Tagging the component (see [Step 1](/roadmap/releases/#step-1-update-code-and-run-the-release-tool))
starts a CI job that eventually results in an artifact being made available for public download.
Please see the [CI flow diagrams](https://github.com/deis/jenkins-jobs/#flow) for details.

Double-check that the artifact is available, either by a `docker pull` command or by running the
appropriate installer script.

If the artifact can't be downloaded, ensure that its CI release jobs are still in progress, or
fix whatever issue arose in the pipeline. For example, the
[master merge pipeline](https://github.com/deis/jenkins-jobs/#when-a-component-pr-is-merged-to-master)
may have failed to promote the `:git-abc1d23` candidate image and needs to be restarted with
that component and commit.

If the component has a correlating [Kubernetes Helm][] chart,
this chart will also be packaged, signed and uploaded to its production chart repo.  Please
verify it can be fetched (and verified):

```
$ helm repo add controller https://charts.deis.com/controller
"controller" has been added to your repositories
$ helm fetch --verify controller/controller --version v2.11.0
Verification: &{0xc420776190 sha256:97116498fcb5bd9da791d26337694bf64fc20815b3e5c0ae3c543def4404f31e controller-v2.11.0.tgz}
```

## How to Release Workflow

Deis Workflow integrates multiple component releases together with a [Kubernetes Helm][] chart
deliverable. This section leads a maintainer through creating a Workflow release.

### Step 1: Set Environment Variables

Export two environment variables that will be used in later steps:

```bash
export WORKFLOW_RELEASE=v2.11.0 WORKFLOW_PREV_RELEASE=v2.10.0  # for example
```

### Step 2: Tag Supporting Repositories

Some Workflow components not in the Helm chart must also be tagged in sync with the release.
Follow the [component release process](#how-to-release-a-component) above and ensure that
these components are tagged:

- [deis/workflow-cli][]
- [deis/workflow-e2e][]

The version number for [deis/workflow-cli][] should always match the overall Workflow version
number.

### Step 3: Create Helm Chart

To create and stage a release candidate chart for Workflow, we will build the [workflow-chart-stage](https://ci.deis.io/job/workflow-chart-stage) job with the following parameters:

`CHART_REPO_TYPE=staging` and `RELEASE_TAG=$WORKFLOW_RELEASE`

This job will gather all of the latest component release tags and use these to specify the versions of all component charts.
It will then package the Workflow chart, upload it to the staging chart repo and kick off an e2e run against said chart.

### Step 4: Manual Testing

Now it's time to go above and beyond current CI tests. Create a testing matrix spreadsheet (copying
from the previous document is a good start) and sign up testers to cover all permutations.

Testers should pay special attention to the overall user experience, make sure upgrading from
earlier versions is smooth, and cover various storage configurations and Kubernetes versions and
infrastructure providers.

When showstopper-level bugs are found, the process is as follows:

1. Create a component PR that fixes the bug.
1. Once the PR passes and is reviewed, merge it and do a new
  [component release](#how-to-release-a-component)
1. Trigger the same `workflow-chart-stage` job as mentioned in Step 3 to upload the newly-generated Workflow release candidate chart to staging.

### Step 5: Release the Chart

When testing has completed without uncovering any new showstopper bugs, kick off the [workflow-chart-release](https://ci.deis.io/job/workflow-chart-release) job with the following parameter:

`RELEASE_TAG=$WORKFLOW_RELEASE`

This job will copy the release candidate chart (now approved by CI and manual testing) from the staging repo to the production repo, signing
it if it has not done so already.

### Step 6: Assemble Master Changelog

Each component already updated its release notes on GitHub with CHANGELOG content. We'll now
generate the master changelog for the Workflow chart, consisting of all aforementioned component changes
as well as those non-component repo changes needing to be manually added.

We'll employ the `requirements.lock` file from the `WORKFLOW_PREV_RELEASE` chart, as well as a repo-to-chart-name mapping file
(see [here](https://github.com/deis/deisrel/blob/master/README.md#usage) for an example), this time invoking `deisrel changelog global` to get all component changes between
the chart versions existing in the `WORKFLOW_PREV_RELEASE` chart and the _most recent_ releases existing in GitHub.
(Therefore, if there are any unreleased commits in a component repo, they will not appear here):

```bash
helm repo add deis https://charts.deis.com/workflow
helm fetch --untar deis/workflow --version $WORKFLOW_PREV_RELEASE
deisrel changelog global workflow/requirements.lock mapping.json > changelog-$WORKFLOW_RELEASE.md
```

To get non-component repo changelogs (presumably tagged in Step 3 above), one can issue a command like the following
which grabs the latest release body from GitHub:

```bash
for repo in workflow workflow-cli workflow-e2e; do
  printf "$repo\n\n"
  printf "$(curl -s https://api.github.com/repos/deis/$repo/releases/latest | jq .body | sed 's/"//g')\n\n"
done
```

These can be added to the `$WORKFLOW_RELEASE` file created previously.

This master changelog should then be placed into a single gist.  The file will also be added to the documentation
update PR created in the next step.

### Step 7: Update Documentation

Create a new pull request at [deis/workflow][] that updates version references to the new release.
Use `git grep $WORKFLOW_PREV_RELEASE` to find any references, but be careful not to change
`CHANGELOG.md`.

Place the `$WORKFLOW_RELEASE` master changelog generated in Step 7 in the `changelogs` directory.
Make sure to add a header to the page to make it clear that this is for a Workflow release, e.g.:

```
## Workflow v2.10.0 -> v2.11.0
```

Once the PR has been reviewed and merged, do a [component release](#how-to-release-a-component) of
[deis/workflow][] itself. The version number for [deis/workflow][] should always match the
overall Workflow version number.

### Step 8: Close GitHub Milestones

Create a pull request at [seed-repo](https://github.com/deis/seed-repo) to close the release
milestone and create the next one. When changes are merged to seed-repo, milestones on all
relevant projects will be updated. If there are open issues attached to the milestone, move them
to the next upcoming milestone before merging the pull request.

Milestones map to Deis Workflow releases in [deis/workflow][]. These milestones do not correspond
to individual component release tags.

### Step 9: Release Workflow CLI Stable

Now that the `$WORKFLOW_RELEASE` version of Workflow CLI has been vetted, we can push `stable` artifacts based on this version.

Kick off https://ci.deis.io/job/workflow-cli-build-stable/ with the `TAG` build parameter of `$WORKFLOW_RELEASE`
and then verify `stable` artifacts are available and appropriately updated after the job completes:

```
$ curl -sSL http://deis.io/deis-cli/install-v2.sh | bash
$ ./deis version
# (Should show $WORKFLOW_RELEASE)
```

### Step 10: Let Everyone Know

Let the rest of the team know they can start blogging and tweeting about the new Workflow release.
Post a message to the #company channel on Slack. Include a link to the released chart and to the
master CHANGELOG:

```
@here Deis Workflow v2.11.0 is now live!
Master CHANGELOG: https://deis.com/docs/workflow/changelogs/v2.11.0/
```

You're done with the release. Nice job!

[component release]: /roadmap/releases/#how-to-release-a-component
[continuous delivery]: https://en.wikipedia.org/wiki/Continuous_delivery
[deis/workflow]: https://github.com/deis/workflow
[deis/workflow-cli]: https://github.com/deis/workflow-cli
[deis/workflow-e2e]: https://github.com/deis/workflow-e2e
[deisrel]: https://github.com/deis/deisrel
[Kubernetes Helm]: https://github.com/kubernetes/helm
[semantic version]: http://semver.org
