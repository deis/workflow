# Submitting a Pull Request

Proposed changes to Deis projects are made as GitHub pull requests.

## Design Document

Before opening a pull request, ensure your change also references a design document if the contribution is substantial. For more information, see [Design Documents](design-documents.md).

## Single Issue

It's hard to reach agreement on the merit of a PR when it isn't focused. When fixing an issue or implementing a new feature, resist the temptation to refactor nearby code or to fix that potential bug you noticed. Instead, open a separate issue or pull request. Keeping concerns separated allows pull requests to be tested, reviewed, and merged more quickly.

Squash and rebase the commit or commits in your pull request into logical units of work with `git`. Include tests and documentation changes in the same commit, so that a revert would remove all traces of the feature or fix.

Most pull requests will reference a GitHub issue. In the PR description - not in the commit itself - include a line such as "closes #1234". The issue referenced will automatically be closed when your PR is merged.


## Include Tests

If you alter or add functionality to any Deis component, your changes should include the necessary tests to prove that it works. Unit tests may be written with the component's implementation language (usually Go or Python), and functional and integration tests are written in Go.

Integration test code spanning multiple Deis components can be found in the `tests/` directory of the [deis/workflow][workflow] project.

While working on local code changes, always run the tests.  Be sure your proposed changes pass all of `./tests/bin/test-integration` on your workstation before submitting a PR.

See [testing](testing.md) for more information.


## Include Docs

Changes to any Deis component that could affect a user's experience also require a change or addition to the relevant documentation. For most Deis components, this involves updating the component's _own_ documentation. In some cases where a component is tightly integrated into [deis/workflow][workflow], its documentation must also be updated.


## Code Standards

Deis components are implemented in [Go][] and [Python][]. For both languages, we agree with [The Zen of Python][zen], which emphasizes simple over clever. Readability counts.

Go code should always be run through `gofmt` on the default settings. Lines of code may be up to 99 characters long. Documentation strings and tests are required for all exported functions. Use of third-party go packages should be minimal, but when doing so, such dependencies should be managed via the [glide][] tool.

Python code should always adhere to [PEP8][], the python code style guide, with the exception that lines of code may be up to 99 characters long. Docstrings and tests are required for all public methods, although the [flake8][] tool used by Deis does not enforce this.

## Commit Style

git commit messages must follow this format:

    {type}({scope}): {subject}
    <BLANK LINE>
    {body}
    <BLANK LINE>
    {footer}

### Example

    feat(workflow): add frobnitz pipeline spout discovery

    Introduces a FPSD component compatible with the industry standard for
    spout discovery.

    BREAKING CHANGE: Fixing the buffer overflow in the master subroutine
        required losing compatibility with the UVEX-9. Any UVEX-9 or
        umVEX-8 series artifacts will need to be updated to umVX format
        with the consortium or vendor toolset.

### Subject Line

The first line of a commit message is its subject. It contains a brief description of the change, no longer than 50 characters.

These `{types}` are allowed:

- **feat** -> feature
- **fix** -> bug fix
- **docs** -> documentation
- **style** -> formatting
- **ref** -> refactoring code
- **test** -> adding missing tests
- **chore** -> maintenance

The `{scope}` specifies the location of the change, such as "Dockerfile," "tests", or "manifests". The `{subject}` should use an imperative, present-tense verb: "change," not "changes" or "changed." Don't capitalize the verb or add a period (.) at the end of the subject line.

### Message Body

Separate the message body from the subject with a blank line. It includes the motivation for the change and points out differences from previous behavior. The body and the footer should be written as full sentences.

### Message Footer

Separate a footer from the message body with a blank line. Mention any breaking change along with the justification and migration notes. If the changes cannot be tested by Deis' test scripts, include specific instructions for manual testing.


## Merge Approval

Any code change - other than a simple typo fix or one-line documentation change - requires at least two [Deis maintainers][maintainers] to accept it.  Maintainers tag pull requests with "**LGTM1**" and "**LGTM2**" (Looks Good To Me) labels to indicate acceptance.

No pull requests can be merged until at least one core maintainer signs off with an LGTM. The other LGTM can come from either a core maintainer or contributing maintainer.

If the PR is from a Deis maintainer, then he or she should be the one to close it. This keeps the commit stream clean and gives the maintainer the benefit of revisiting the PR before deciding whether or not to merge the changes.

[go]: http://golang.org/
[glide]: https://github.com/Masterminds/glide
[flake8]: https://pypi.python.org/pypi/flake8/
[maintainers]: maintainers.md
[pep8]: http://www.python.org/dev/peps/pep-0008/
[python]: http://www.python.org/
[zen]: http://www.python.org/dev/peps/pep-0020/
[workflow]: https://github.com/deis/workflow
