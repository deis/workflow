# CLI Plugins

Plugins allow developers to extend the functionality of the [Deis Client][], adding new commands or features.

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

[deis client]: ../using-deis/installing-the-client.md
