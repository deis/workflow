# Deis Workflow Roadmap

The Deis Workflow Roadmap is a community document created as part of the open
[Planning Process](planning-process.md). Each roadmap item describes a high-level capability or
grouping of features that are deemed important to the future of Deis.

Given the project's rapid [Release Schedule](releases.md), roadmap
items are designed to provide a sense of direction over many releases.

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

* [ ] Define and deliver alerts with Kapacitor: <https://github.com/deis/monitor/issues/44>

## Workflow Addons/Services

Developers should be able to quickly and easily provision application
dependencies using a services or addon abstraction.
<https://github.com/deis/deis/issues/231>

## Inbound/Outbound Webhooks

Deis Workflow should be able to send and receive webhooks from external
systems. Facilitating integration with third party services like GitHub,
Gitlab, Slack, Hipchat.

* [X] Send webhook on platform events: <https://github.com/deis/deis/issues/1486> (Workflow v2.10)
