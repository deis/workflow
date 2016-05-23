# Troubleshooting Workflow

Common issues that users have run into when provisioning Workflow are detailed below.

## A Component Fails to Start

For information on troubleshooting a failing component, see
[Troubleshooting with Kubectl][kubectl].

## Permission denied (publickey)

The most common problem for this issue is the user forgetting to run `deis keys:add` or add their
private key to their SSH agent. To do so, run `ssh-add ~/.ssh/id_rsa` and try running
`git push deis master` again.

## Other Issues

Running into something not detailed here? Please [open an issue][issue] or hop into
[#community on Slack][slack] for help!

[kubectl]: kubectl.md
[issue]: https://github.com/deis/workflow/issues/new
[slack]: http://slack.deis.io/
