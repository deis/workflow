# Extending Workflow

Deis Workflow is an open source project which wouldn't be here without the amazing skill
and enthusiasm of the community that has grown up around it. Several projects have blossomed
which extend Workflow in various ways.

These links are to community-contributed extensions of Deis Workflow. Deis makes no
guarantees about the functionality, security, or code contained within. As with any software,
use with caution in a production environment.

## Workflow Community Projects

- [alea][] is a backing services manager for Deis Workflow, providing easy
  access to PostgreSQL, Redis, MongoDB, and memcached.
- [deisdash][] is a web-based UI supporting many user and app actions without need of the
  `deis` command-line interface.
- [deis-cleanup][] is a Deis-friendly, configurable approach to purging unneeded Docker
  containers and images.
- [deis-global-config-plugin][] stores config values in [Vault][] for easy use in Workflow apps.
- [deis-node][] is a controller API client for a browser in NodeJS.
- [deis-ui][] is the beginning of a full client-side dashboard that interfaces with the
  controller API.
- [deis-workflow-aws][] simplifies installing Workflow on [Amazon Web Services][], backed by
  S3 and using ECR as the container registry.
- [deis-workflow-gke][] simplifies installing Workflow on [Google Container Engine][], backed
  by Google Cloud Storage and using gcr.io as the container registry.
- [deis-workflow-ruby][] contains Workflow controller API bindings for Ruby programming.
- [heroku-to-deis][] migrates existing Heroku applications to the Workflow platform.
- [kube-solo-osx][] creates a zero-to-Kubernetes development environment for macOS in under
  two minutes, with specific support for installing Workflow with [Helm][] or Helm Classic.

Are we missing something? Please open a [documentation pull request][] to add it.

[alea]: https://github.com/Codaisseur/alea
[Amazon Web Services]: https://aws.amazon.com/
[deisdash]: https://github.com/olalonde/deisdash
[deis-cleanup]: https://github.com/Ragnarson/deis-cleanup
[deis-global-config-plugin]: https://github.com/Rafflecopter/deis-global-config-plugin
[deis-node]: https://github.com/olalonde/deis-node
[deis-ui]: https://github.com/jumbojett/deis-ui
[deis-workflow-aws]: https://github.com/rimusz/deis-workflow-aws
[deis-workflow-gke]: https://github.com/rimusz/deis-workflow-gke
[deis-workflow-ruby]: https://github.com/thomas0087/deis-workflow-ruby
[documentation pull request]: https://github.com/deis/workflow/pulls
[Google Container Engine]: https://cloud.google.com/container-engine/
[Helm]: https://github.com/kubernetes/helm
[heroku-to-deis]: https://github.com/emartech/heroku-to-deis
[kube-solo-osx]: https://github.com/TheNewNormal/kube-solo-osx
[Vault]: https://www.vaultproject.io/
