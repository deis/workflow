# Submitting a Pull Request

Proposed changes to Deis are made as GitHub [pull requests][pr].

## Design Document

Before opening a pull request, ensure your change also references a design document if the contribution is substantial. For more information, see [design documents](design-documents.md).

## Single Issue

When fixing or implementing a GitHub issue, resist the temptation to refactor nearby code or to fix that potential bug you noticed. Instead, open a new [pull request][pr] just for that change.

It's hard to reach agreement on the merit of a PR when it isn't focused. Keeping concerns separated allows pull requests to be tested, reviewed, and merged more quickly.

Squash and rebase the commit or commits in your pull request into logical units of work with `git`. Include tests and documentation changes in the same commit, so that a revert would remove all traces of the feature or fix.

Most pull requests will reference a [GitHub issue][issue]. In the PR description - not in the commit itself - include a line such as "closes #1234". The issue referenced will then be closed when your PR is merged.


## Include Tests

If you change or add functionality to any Deis code, your changes should include the necessary tests to prove that it works. Unit tests may be written with the component's implementation language (usually Go or Python), and functional and integration tests are written in Go. Test code can be found in the `tests/` directory of the Deis project.

While working on local code changes, always run the tests.  Be sure your proposed changes pass all of `./tests/bin/test-integration` on your workstation before submitting a PR.

See [testing](testing.md) for more information.


## Include Docs

Any change to Deis that could affect a user's experience also needs a change or addition to the relevant documentation. Deis generates the HTML documentation hosted at <http://docs.deis.io/> from the text markup sources in the `docs/` directory.

See [the README](https://github.com/deis/deis/blob/master/docs/README.md) for more information.


## Code Standards

Deis is a [Go][] and [Python][] project. For both languages, we agree with [The Zen of Python][zen], which emphasizes simple over clever. Readability counts.

Go code should always be run through `gofmt` on the default settings. Lines of code may be up to 99 characters long. Documentation strings and tests are required for all public methods. Use of third-party go packages should be minimal, but when doing so, vendor code into the Deis package with the [godep][] tool.

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

!!! note
    You can install a git hook that checks your commit message format with `make commit-hook`.

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

The `{scope}` specifies the location of the change, such as "controller," "tests", or "contrib". The `{subject}` should use an imperative, present-tense verb: "change," not "changes" or "changed." Don't capitalize the verb or add a period (.) at the end of the subject line.

### Message Body

Separate the message body from the subject with a blank line. It includes the motivation for the change and points out differences from previous behavior. The body and the footer should be written as full sentences.

### Message Footer

Separate a footer from the message body with a blank line. Mention any breaking change along with the justification and migration notes. If the changes cannot be tested by Deis' test scripts, include specific instructions for manual testing.


## Merge Approval

[Deis maintainers][maintainers] add "**LGTM**" (Looks Good To Me) or an equivalent comment to indicate that a PR is acceptable. Any code change - other than a simple typo fix or one-line documentation change - requires at least two maintainers to accept it.

No pull requests can be merged until at least one core maintainer signs off with an LGTM. The other LGTM can come from either a core maintainer or contributing maintainer.

If the PR is from a Deis maintainer, then he or she should be the one to close it. This keeps the commit stream clean and gives the maintainer the benefit of revisiting the PR before deciding whether or not to merge the changes.

[go]: http://golang.org/
[godep]: https://github.com/tools/godep
[flake8]: https://pypi.python.org/pypi/flake8/
[issue]: https://github.com/deis/deis/issues
[maintainers]: https://github.com/deis/deis/blob/master/MAINTAINERS.md
[pep8]: http://www.python.org/dev/peps/pep-0008/
[pr]: https://github.com/deis/deis/pulls
[python]: http://www.python.org/
[zen]: http://www.python.org/dev/peps/pep-0020/
