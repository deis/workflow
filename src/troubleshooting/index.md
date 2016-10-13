# Troubleshooting Workflow

Common issues that users have run into when provisioning Workflow are detailed below.

## A Component Fails to Start

For information on troubleshooting a failing component, see
[Troubleshooting with Kubectl][kubectl].

## An Application Fails to Start

For information on troubleshooting application deployment issues, see
[Troubleshooting Applications][troubleshooting-app].


## Permission denied (publickey)

The most common problem for this issue is the user forgetting to run `deis keys:add` or add their
private key to their SSH agent. To do so, run `ssh-add ~/.ssh/id_rsa` and try running
`git push deis master` again.

If you happen get a `Could not open a connection to your authentication agent` 
error after trying to run `ssh-add` command above, you may need to load the SSH
agent environment variables issuing the `eval "$(ssh-agent)"` command before.

## Other Issues

Running into something not detailed here? Please [open an issue][issue] or hop into
[#community on Slack][slack] for help!

[kubectl]: kubectl.md
[issue]: https://github.com/deis/workflow/issues/new
[slack]: http://slack.deis.io/
[troubleshooting-app]: applications.md
