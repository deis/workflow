# Registering a User

To use Deis, you must first register a user on the [Controller][].


## Register with a Controller

Use `deis register` with the [Controller][] URL (supplied by your Deis administrator)
to create a new account. After successful registration you will be logged in as the new user.

    $ deis register http://deis.example.com
    username: myuser
    password:
    password (confirm):
    email: myuser@example.com
    Registered myuser
    Logged in as myuser

!!! important
    The first user to register with Deis Workflow is automatically becomes a
    "superuser". Additional users who register will be ordinary users. It's also
    possible to disable user registration after creating the superuser account.

## Login to Workflow

If you already have an account, use `deis login` to authenticate against the Deis Workflow API.

    $ deis login http://deis.example.com
    username: deis
    password:
    Logged in as deis

## Logout from Workflow

Logout of an existing controller session using `deis logout`.

    $ deis logout
    Logged out as deis

## Verify your session

You can verify your client configuration by running `deis whoami`.

    $ deis whoami
    You are deis at http://deis.example.com

!!! note
    Session and client configuration is stored in the `~/.deis/client.json` file.

[controller]: ../understanding-workflow/components.md#controller
[router]: ../understanding-workflow/components.md#router
