# How to Contribute

Deis components are Apache 2.0 licensed and accept contributions via Github pull requests. This document outlines resources and conventions useful for anyone wishing to contribute either by reporting issues or submitting pull requests.

# Certificate of Origin

By contributing to any Deis project you agree to its [Developer Certificate of Origin (DCO)][dco]. This document was created by the Linux Kernel community and is a simple statement that you, as a contributor, have the legal right to make the contribution.

# Support Channels

Before opening a new issue or PR against any Deis project, it's helpful to search that project's issue queue - it's likely that another user has already reported the issue you're facing, or it's a known issue that we're already aware of.

A consolidated view of open issues and pull requests for all Deis projects is available [here][issues].

Additionally, see the [Troubleshooting][] documentation for common issues.

Our official support channels are:

- GitHub issue queues:
  - builder: https://github.com/deis/builder/issues
  - chart: https://github.com/deis/charts/issues
  - controller: https://github.com/deis/controller/issues
  - database: https://github.com/deis/postgres/issues
  - documentation: https://github.com/deis/workflow/issues
  - helm classic: https://github.com/helm/helm-classic/issues
  - minio: https://github.com/deis/minio/issues
  - registry: https://github.com/deis/registry/issues
  - router: https://github.com/deis/router/issues
  - All other public [Deis repositories][repos]
- The [Deis #community Slack channel](https://slack.deis.io)

## Getting Started

The [Development Environment][dev-environment] documentation extensively details procedures for setting up a development environment and outlines the contribution workflow.

[Submitting a Pull Request][pr] documents stylistic conventions that help Deis maintainers to more easily review and accept your PRs.

[dco]: DCO
[issues]: https://github.com/pulls?utf8=%E2%9C%93&q=is%3Aopen+user%3Adeis+user%3Ahelm
[repos]: https://github.com/deis
[troubleshooting]: src/troubleshooting/troubleshooting.md
[dev-environment]: src/contributing/development-environment.md
[pr]: src/contributing/submitting-a-pull-request.md
