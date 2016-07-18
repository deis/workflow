# Release Schedule

Some of the greatest assets of the Deis team are velocity and agility. Workflow changed rapidly and
with relative ease during initial development.

Deis now harnesses those strengths into powering a regular, public release cadence. From v2.0.0
onward, the Deis team will release a minor version every 2 weeks, with patch versions as needed.
The project will use GitHub milestones to communicate the content and timing of major and minor
releases.

Deis releases are not feature-based, in that dates are not linked to specific features. If a
feature is merged before the release date, it is included in the next minor or major release.

The master `git` branch of Deis should always work. Only changes considered ready to be released
publicly are merged, and non-patch releases are cut from master.

## Semantic Versioning

Deis releases comply with [semantic versioning][], with the "public API" broadly
defined as:

- the REST API for [the Controller][controller]
- `deis` CLI commands and options

Users of Workflow can be confident that upgrading to a patch or to a minor release will not change
the behavior of these items in a backward-incompatible way.

## Release Criteria

For any Workflow release to be made publicly available, it must meet at least these criteria:

- Passes all tests on the supported, load-balancing cloud providers
- Has no new regressions in behavior that are not considered trivial

## Patch Releases

A patch release of Workflow includes backwards-compatible bug fixes. Upgrading to this version is
safe and can be done in-place.

Backwards-compatible bug fixes to Workflow are merged into the master branch at any time after they
have [two approval comments][merge approval].

Patch releases are created as often as needed, based on the priority of one or more bug fixes that
have been merged. If time or severity is crucial, an individual maintainer can create a patch
release without consensus from others. Patch releases are created from a previous release by
cherry-picking specific bug fixes from the master branch to the release branch, then applying and
pushing the new release tag.

## Minor Releases

A minor release of Workflow introduces functionality in a backward-compatible manner. Upgrading to
this version is safe and can be done in-place.

Backwards-compatible functionality changes to Workflow are merged into the master branch after they
have [two approval comments][merge approval], and after the PR has been assigned to a milestone
tracking the minor release.

It is preferable to merge several backwards-compatible functionality changes for a single minor
release.

The Deis team will use GitHub milestones to communicate the content and timing of planned minor
releases.

A minor release may be superceded by a major release.

## Major Releases

A major release of Workflow introduces incompatible API changes. Custom integrations with Workflow
may need to be updated.

Incompatible changes to Workflow are merged into the master branch deliberately, by agreement among
maintainers. In addition to [two approval comments][merge approval], the pull request must be
assigned to a planning milestone for that release, at which point it can be merged when release
activities and testing begin.

The Deis team will use GitHub milestones to communicate the content and timing of planned major
releases.


[controller]: ../understanding-workflow/components.md#controller
[merge approval]: ../contributing/submitting-a-pull-request.md#merge-approval
[semantic versioning]: http://semver.org/spec/v2.0.0.html
