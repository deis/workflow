# Submitting a Pull Request

Proposed changes to Deis projects are made as GitHub pull requests.

## Design Document

Before opening a pull request, ensure your change also references a design document if the contribution is substantial. For more information, see [Design Documents](design-documents.md).

## Single Issue

It's hard to reach agreement on the merit of a PR when it isn't focused. When fixing an issue or implementing a new feature, resist the temptation to refactor nearby code or to fix that potential bug you noticed. Instead, open a separate issue or pull request. Keeping concerns separated allows pull requests to be tested, reviewed, and merged more quickly.

Squash and rebase the commit or commits in your pull request into logical units of work with `git`. Include tests and documentation changes in the same commit, so that a revert would remove all traces of the feature or fix.

Most pull requests will reference a GitHub issue. In the PR description - not in the commit itself - include a line such as "closes #1234". The issue referenced will automatically be closed when your PR is merged.


## Include Tests

If you significantly alter or add functionality to a component that impacts the broader Deis Workflow PaaS, you should submit a complementary PR to modify or amend end-to-end integration tests.  These integration tests can be found in the [deis/workflow-e2e][workflow-e2e] repository.

See [testing](testing.md) for more information.


## Include Docs

Changes to any Deis Workflow component that could affect a user's experience also require a change or addition to the relevant documentation. For most Deis components, this involves updating the component's _own_ documentation. In some cases where a component is tightly integrated into [deis/workflow][workflow], its documentation must also be updated.

## Cross-repo commits

If a pull request is part of a larger piece of work involving one or more additional commits in other Workflow repositories, these commits can be referenced in the last PR to be submitted.  The downstream [e2e test job](https://ci.deis.io/job/workflow-test-pr/) will then supply every referenced commit (derived from PR issue number supplied) to the test runner so it can source the necessary Docker images for inclusion in the generated Workflow chart to be tested.

For example, consider paired commits in [deis/controller](https://github.com/deis/controller) and [deis/workflow-e2e](https://github.com/deis/workflow-e2e).  The commit body for the first PR in `deis/workflow-e2e` would look like:

```
feat(foo_test): add e2e test for feature foo

[skip e2e] test for controller#42
```
Adding `[skip e2e]` forgoes the e2e tests on this commit. This and any other required PRs aside from the final PR should be submitted first, so that their respective build and image push jobs run.

Lastly, the final PR in `deis/controller` should be created with the required PR number(s) listed, in the form of `[Rr]equires <repoName>#<pullRequestNumber>`, for use by the downstream e2e run.

```
feat(foo): add feature foo

Requires workflow-e2e#42
```

## Code Standards

Deis components are implemented in [Go][] and [Python][]. For both languages, we agree with [The Zen of Python][zen], which emphasizes simple over clever. Readability counts.

Go code should always be run through `gofmt` on the default settings. Lines of code may be up to 99 characters long. Documentation strings and tests are required for all exported functions. Use of third-party go packages should be minimal, but when doing so, such dependencies should be managed via the [glide][] tool.

Python code should always adhere to [PEP8][], the python code style guide, with the exception that lines of code may be up to 99 characters long. Docstrings and tests are required for all public methods, although the [flake8][] tool used by Deis does not enforce this.

## Commit Style

We follow a convention for commit messages borrowed from CoreOS, who borrowed theirs
from AngularJS. This is an example of a commit:

```
feat(scripts/test-cluster): add a cluster test command

this uses tmux to setup a test cluster that you can easily kill and
start for debugging.
```

To make it more formal, it looks something like this:

```
{type}({scope}): {subject}
<BLANK LINE>
{body}
<BLANK LINE>
{footer}
```

The allowed `{types}` are as follows:

* `feat` -> feature
* `fix` -> bug fix
* `docs` -> documentation
* `style` -> formatting
* `ref` -> refactoring code
* `test` -> adding missing tests
* `chore` -> maintenance

The `{scope}` can be anything specifying the location(s) of the commit change(s).

The `{subject}` needs to be an imperative, present tense verb: “change”, not “changed” nor
“changes”. The first letter should not be capitalized, and there is no dot (.) at the end.

Just like the `{subject}`, the message `{body}` needs to be in the present tense, and includes
the motivation for the change, as well as a contrast with the previous behavior. The first
letter in a paragraph must be capitalized.

All breaking changes need to be mentioned in the `{footer}` with the description of the
change, the justification behind the change and any migration notes required.

Any line of the commit message cannot be longer than 72 characters, with the subject line
limited to 50 characters. This allows the message to be easier to read on GitHub as well
as in various git tools.

## Merge Approval

Any code change - other than a simple typo fix or one-line documentation change - requires at least two [Deis maintainers][maintainers] to accept it.  Maintainers tag pull requests with "**LGTM1**" and "**LGTM2**" (Looks Good To Me) labels to indicate acceptance.

No pull requests can be merged until at least one core maintainer signs off with an LGTM. The other LGTM can come from either a core maintainer or contributing maintainer.

If the PR is from a Deis maintainer, then he or she should be the one to close it. This keeps the commit stream clean and gives the maintainer the benefit of revisiting the PR before deciding whether or not to merge the changes.

An exception to this is when an errant commit needs to be reverted urgently. If necessary, a PR that only reverts a previous commit can be merged without waiting for LGTM approval.

[go]: http://golang.org/
[glide]: https://github.com/Masterminds/glide
[flake8]: https://pypi.python.org/pypi/flake8/
[maintainers]: maintainers.md
[pep8]: http://www.python.org/dev/peps/pep-0008/
[python]: http://www.python.org/
[zen]: http://www.python.org/dev/peps/pep-0020/
[workflow]: https://github.com/deis/workflow
[workflow-e2e]: https://github.com/deis/workflow-e2e
