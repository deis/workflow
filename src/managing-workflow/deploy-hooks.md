# Deploy Hooks

Deploy hooks allow an external service to receive a notification whenever a new version of your app
is pushed to Workflow. It’s useful to help keep the development team informed about deploys, while
it can also be used to integrate different systems together.

After one or more hooks are setup, hook output and errors appear in your application’s logs:

```
$ deis logs
...
2011-03-15T15:07:29-07:00 deis[api]: Deploy hook sent to http://deis.rocks
```

Deploy hooks are a generic HTTP hook. An administrator can create and configure multiple deploy
hooks by [tuning the controller settings][controller-settings] via the Helm chart.

## HTTP POST Hook

The HTTP deploy hook performs an HTTP POST to a URL. The parameters included in the request are the
same as the variables available in the hook message: `app`, `release`, `release_summary`, `sha` and
`user`. See below for their descriptions:

```
app=secure-woodland&release=v4&release_summary=gabrtv%20deployed%35b3726&sha=35b3726&user=gabrtv
```

Optionally, if a deploy hook secret key is added to the controller through
[tuning the controller settings][controller-settings], a new `Authorization` header will be
present in the POST request. The value of this header is computed as the [HMAC][] hex digest of the
request URL, using the secret as the key.

In order to authenticate that this request came from Workflow, use the secret key, the full URL and
the HMAC-SHA1 hashing algorithm to compute the signature. In Python, that would look something like
this:

```python
import hashlib
import hmac

hmac.new("my_secret_key", "http://deis.rocks?app=secure-woodland&release=v4&release_summary=gabrtv%20deployed%35b3726&sha=35b3726&user=gabrtv", digestmod=hashlib.sha1).hexdigest()
```

If the value of the computed HMAC hex digest and the value in the `Authorization` header are
identical, then the request came from Workflow.

!!! important
	When computing the signature, ensure that the URL parameters are in alphabetic order. This is
	critical when computing the cryptographic signature as most web applications don't care about
	the order of the HTTP parameters, but the cryptographic signature will not be the same.


[controller-settings]: tuning-component-settings.md#customizing-the-controller
[hmac]: https://en.wikipedia.org/wiki/Hash-based_message_authentication_code
