# Deis Workflow  CLI

The Deis Workflow command-line interface (CLI), or client, allows you to interact
with Deis Workflow.

## Installation

Install the latest `deis` client for Linux or Mac OS X with:

    $ curl -sSL http://deis.io/deis-cli/install-v2.sh | bash

The installer puts `deis` in your current directory, but you should move it
somewhere in your $PATH:

    $ ln -fs $PWD/deis /usr/local/bin/deis

## Getting Help

The Deis client comes with comprehensive documentation for every command.
Use `deis help` to explore the commands available to you:

    $ deis help
    The Deis command-line client issues API calls to a Deis controller.

    Usage: deis <command> [<args>...]

    Auth commands::

      register      register a new user with a controller
      login         login to a controller
      logout        logout from the current controller

    Subcommands, use `deis help [subcommand]` to learn more::
    ...

To get help on subcommands, use `deis help [subcommand]`:

    $ deis help apps
    Valid commands for apps:

    apps:create        create a new application
    apps:list          list accessible applications
    apps:info          view info about an application
    apps:open          open the application in a browser
    apps:logs          view aggregated application logs
    apps:run           run a command in an ephemeral app container
    apps:destroy       destroy an application

    Use `deis help [command]` to learn more


## Support for Multiple Profiles

The CLI reads from the default `client` profile, which is located on your
workstation at `$HOME/.deis/client.json`.

Easily switch between multiple Deis Workflow installations or users by setting
the `$DEIS_PROFILE` environment variable or by using the `-c` flag.

There are two ways to set the `$DEIS_PROFILE` option.

1. Path to a json configuration file.
2. Profile name. If you set profile to just a name, it will be saved alongside the default profile,
   in `$HOME/.deis/<name>.json`.

Examples:

    $ DEIS_PROFILE=production deis login deis.production.com
    ...
    Configuration saved to /home/testuser/.deis/production.json
    $ DEIS_PROFILE=~/config.json deis login deis.example.com
    ...
    Configuration saved to /home/testuser/config.json

The configuration flag works identically to and overrides `$DEIS_PROFILE`:

    $ deis whoami -c ~/config.json
    You are deis at deis.example.com

## Proxy Support

If your workstation uses a proxy to reach the network where the cluster lies,
set the `http_proxy` or `https_proxy` environment variable to enable proxy support:

    $ export http_proxy="http://proxyip:port"
    $ export https_proxy="http://proxyip:port"

!!! note
    Configuring a proxy is generally not necessary for local Vagrant clusters.

## CLI Plugins

Plugins allow developers to extend the functionality of the Deis Client, adding new commands or features.

If an unknown command is specified, the client will attempt to execute the command as a dash-separated command. In this case, `deis resource:command` will execute `deis-resource` with the argument list `command`. In full form:

    $ # these two are identical
    $ deis accounts:list
    $ deis-accounts list

Any flags after the command will also be sent to the plugin as an argument:

    $ # these two are identical
    $ deis accounts:list --debug
    $ deis-accounts list --debug

But flags preceding the command will not:

    $ # these two are identical
    $ deis --debug accounts:list
    $ deis-accounts list
