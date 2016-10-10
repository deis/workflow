# Triaging Issues

Issue triage provides an important way to contribute to an open source project.  Triage helps ensure issues resolve quickly by:

- Describing the issue's intent and purpose is conveyed precisely. This is necessary because it can be difficult for an issue to explain how an end user experiences an problem and what actions they took.
- Giving a contributor the information they need before they commit to resolving an issue.
- Lowering the issue count by preventing duplicate issues.
- Streamlining the development process by preventing duplicate discussions.

If you don't have time to code, consider helping with triage. The community will thank you for saving them time by spending some of yours.

## Ensure the Issue Contains Basic Information

Before triaging an issue very far, make sure that the issue's author provided the standard issue information. This will help you make an educated recommendation on how this to categorize the issue. Standard information that should be included in most issues are things such as:

-   the version(s) of Deis this issue affects
-   a reproducible case if this is a bug
-   page URL if this is a docs issue or the name of a man page

Depending on the issue, you might not feel all this information is needed. Use your best judgment. If you cannot triage an issue using what its author provided, explain kindly to the author that they must provide the above information to clarify the problem.

If the author provides the recommended information but you are still unable to triage the issue, request additional information. Do this kindly and politely because you are asking for more of the author's time.

If the author does not respond requested information within the timespan of a week, close the issue with a kind note stating that the author can request for the issue to be reopened when the necessary information is provided.

## Classifying the Issue

An issue can have multiple of the following labels:

### Issue Kind

Kind         | Description
-------------|-----------------------------------------------------------------------------------------------------------------------------
bug          | Bugs are bugs. The cause may or may not be known at triage time so debugging should be taken account into the time estimate.
docs         | Writing documentation, man pages, articles, blogs, or other significant word-driven task.
enhancement  | Enhancements can drastically improve usability or performance of a component.
question     | Contains a user or contributor question requiring a response.
security     | Security-related issues such as TLS encryption, network segregation, authn/authz features, etc.

### Functional Area

- builder
- cache
- contrib and provisioning
- client
- controller
- database
- docs
- kubernetes
- registry
- router
- store (Ceph)
- tests

## Easy Fix

"Easy Fix" issues are a way for a new contributor to find issues that are fit for their experience level. These issues are typically for users who are new to Deis, and possibly Go, and is looking to help while learning the basics.

## Prioritizing issues

When attached to a specific milestone, an issue can be attributed one of the following labels to indicate their degree of priority.

Priority   | Description
-----------|-----------------------------------------------------------------------------------------------------------------------------------
priority&nbsp;0 | Urgent: Security, critical bugs, blocking issues. Drop everything and fix this today, then consider creating a patch release.
priority&nbsp;1 | Serious: Impedes user actions or is a regression. Fix this before the next planned release.

And that's it. That should be all the information required for a new or existing contributor to come in an resolve an issue.
