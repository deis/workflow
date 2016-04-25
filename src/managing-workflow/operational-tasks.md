# Operational Tasks

Below are some common operational tasks for managing the platform.


## Managing users

There are two classes of Workflow users: normal users and administrators.

 * Users can use most of the features of Workflow - creating and deploying applications, adding/removing domains, etc.
 * Administrators can perform all the actions that users can, but they also have owner access to all applications.

The first user created on a Workflow installation is automatically an administrator.


## Promoting users to Administrators

You can use the `deis perms` command to promote a user to an administrator:

    $ deis perms:create john --admin


## Re-issuing User Authentication Tokens

The controller API uses a simple token-based HTTP Authentication scheme. Token authentication is
appropriate for client-server setups, such as native desktop and mobile clients. Each user of the
platform is issued a token the first time that they sign up on the platform. If this token is
compromised, it will need to be regenerated.

A user can regenerate their own token like this:

    $ deis auth:regenerate

An administrator can also regenerate the token of another user like this:

    $ deis auth:regenerate -u test-user

At this point, the user will no longer be able to authenticate against the controller with his auth
token:

    $ deis apps
    401 UNAUTHORIZED
    Detail:
    Invalid token

They will need to log back in to use their new auth token.

If there is a cluster wide security breach, an administrator can regenerate everybody's auth token like this:

    $ deis auth:regenerate --all=true
