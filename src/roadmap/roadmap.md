# Deis Workflow Roadmap

The Deis Workflow Roadmap is a community document created as part of the open
[Planning Process](planning-process.md). Each roadmap item describes a high-level capability or
grouping of features that are deemed important to the future of Deis.

Given the project's rapid [Release Schedule](releases.md), roadmap
items are designed to provide a sense of direction over many releases.

## Deployments

Deis Workflow should use Kubernetes-native constructs wherever possible. By
switching to `Deployments`, the controller component will no longer need to
orchestrate rolling deploys. Instead, controller can delegate that work to
Kubernetes control loops.

* [X] Support Kubernetes Deployments <https://github.com/deis/controller/pull/854> (Workflow 2.2)
* [X] Kubernetes Deployments by default (Workflow 2.4)

## Private Registry and Native IaaS Registry Support

Many users of Deis v1 requested the ability to push and pull application
artifacts from private Docker registries. While v1 supported a
[workaround](https://github.com/deis/deis/issues/2232) or two, operators
usually had to intervene or build custom tooling. Deis Workflow aims to make it
simple to configure your Workflow install to pull and push images to private
registries.

* [X] Pull from private registry <https://github.com/deis/workflow/pull/201> (Workflow 2.0)
* [X] Push to private registry for builder (Workflow 2.3)
* [X] Support native auth strategies for ECR and GCR (Workflow 2.4)

## Application Management

Various application-related features that give developers and operators
flexibility in how applications are managed by the platform:

* [X] Per-process type health checks: <https://github.com/deis/controller/issues/881> (Workflow 2.4)
* [X] Application Maintenance Mode: <https://github.com/deis/deis/issues/3722> (Workflow 2.4)
* [X] Enforce SSL Per-Application: <https://github.com/deis/router/issues/148> (Workflow 2.5)
* [X] Per-application IP Whitelisting via CLI: <https://github.com/deis/controller/issues/240> (Workflow 2.5)
* [ ] Per-application Kubernetes Network Policy:

### Private Application Support

* [X] Private Application Support: <https://github.com/deis/controller/pull/934> (Workflow 2.4)

Related issues:

* <https://github.com/deis/deis/issues/4391>
* <https://github.com/deis/deis/issues/2715>

## Application Autoscaling

Developers should be able to define an autoscaling policy per application
process type. Under the covers, Workflow should use HorizontalPodAutoscaling.

* [X] Application Autoscaling <https://github.com/deis/workflow/issues/403> (Alpha, Workflow 2.5)

## Interactive `deis run /bin/bash`

Provide the ability for developers to launch an interactive terminal session in
their application environment.

Related issues:

* <https://github.com/deis/workflow-cli/issues/98>
* <https://github.com/deis/deis/issues/117>

## Log Streaming

Stream application logs via `deis logs -f` <https://github.com/deis/deis/issues/465>

## Teams and Permissions

Teams and Permissions represents a more flexible permissions model to allow
more nuanced control to applications, capabilities and resources on the
platform. There have been a number of proposals in this area which need to be
reconciled for Deis Workflow before we begin implementation.

Related issues:

* Deploy Keys: <https://github.com/deis/deis/issues/3875>
* Teams: <https://github.com/deis/deis/issues/4173>
* Fine grained permissions: <https://github.com/deis/deis/issues/4150>
* Admins create apps only: <https://github.com/deis/deis/issues/4052>
* Admin Certificate Permissions: <https://github.com/deis/deis/issues/4576#issuecomment-170987223>

## Monitoring

* [ ] deis/controller emitting metrics
* [ ] Define and deliver alerts with Kapacitor: <https://github.com/deis/monitor/issues/44>

## Workflow Addons/Services

Developers should be able to quickly and easily provision application
dependencies using a services or addon abstraction.
<https://github.com/deis/deis/issues/231>

## Inbound/Outbound Webhooks

Deis Workflow should be able to send and receive webhooks from external
systems. Facilitating integration with third party services like GitHub,
Gitlab, Slack, Hipchat.

* [ ] Send webhook on platform events: <https://github.com/deis/deis/issues/1486>
* [ ] Trigger automatic deploy from GitHub Deployments API
