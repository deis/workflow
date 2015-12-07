import requests
import urlparse


def error(response, errmsg, *args):
    # reversing since URL vs Messages are constructed the opposite way
    args = tuple(reversed(args))
    errmsg = errmsg.format(*args)
    errmsg = "failed to {}: {} {}\n{}".format(
        errmsg,
        response.status_code,
        response.reason,
        response.json()
    )
    raise RuntimeError(errmsg)


def error_message(method, url):
    """ Get good error message based on URL and method used """
    errmsg = method
    count = url.count('{}')
    segments = url.strip('/').split('/')

    # Format is /namespace/{}/<resource_type>/{}/<sub_resource>
    # Determine if resource type should be plural or singular
    resource_type = segments[3][0:-1] if count > 1 else segments[3]
    # Check if it is a sub resource
    if len(segments) > 4:
        errmsg += ' %s for' % segments.pop()

    errmsg += ' %s "{}"' % resource_type.capitalize()

    # Requesting a namespaced resource
    if count > 1:
        errmsg += ' in Namespace "{}"'

    return errmsg


def unhealthy(status_code):
    """Status is considered unhealthy if it is not 2xx"""
    if not 200 <= status_code <= 299:
        return True

    return False


class KubeHTTPClient(object):
    version = 'v1'
    session = None

    def __init__(self, target):
        self.target = target

        # TODO singleton this if it makes sense
        if not self.session:
            self.connect()

    def connect(self):
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as token_file:
            token = token_file.read()

        session = requests.Session()
        session.headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        }
        session.verify = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
        self.session = session

    def url(self, tmpl, *args):
        """Return a fully-qualified Kubernetes API URL from a string template with args."""
        url = "/api/{}".format(self.version) + tmpl.format(*args)
        return urlparse.urljoin(self.target, url)

    def get(self, url, *args, **kwargs):
        response = self.session.get(self.url(url, *args), **kwargs)
        check = kwargs.get('check', True)  # Check response and fail
        if check and unhealthy(response.status_code):
            error(response, error_message('get', url), *args)

        return response

    def delete(self, url, *args, **kwargs):
        response = self.session.delete(self.url(url, *args), **kwargs)
        check = kwargs.get('check', True)  # Check response and fail
        if check and unhealthy(response.status_code):
            error(response, error_message('delete', url), *args)

        return response

    def post(self, url, *args, **kwargs):
        response = self.session.post(self.url(url, *args), **kwargs)
        check = kwargs.get('check', True)  # Check response and fail
        if check and unhealthy(response.status_code):
            error(response, error_message('create', url), *args)

        return response

    def put(self, url, *args, **kwargs):
        response = self.session.put(self.url(url, *args), **kwargs)
        check = kwargs.get('check', True)  # Check response and fail
        if check and unhealthy(response.status_code):
            error(response, error_message('update', url), *args)

        return response

    def head(self, url, check=True, *args, **kwargs):
        response = self.session.head(self.url(url, *args), **kwargs)
        check = kwargs.get('check', True)  # Check response and fail
        if check and unhealthy(response.status_code):
            error(response, error_message('head', url), *args)

        return response

    def options(self, url, *args, **kwargs):
        response = self.session.head(self.url(url, *args), **kwargs)
        check = kwargs.get('check', True)  # Check response and fail
        if check and unhealthy(response.status_code):
            error(response, error_message('options', url), *args)

        return response

    def patch(self, url, *args, **kwargs):
        response = self.session.patch(self.url(url, *args), **kwargs)
        check = kwargs.get('check', True)  # Check response and fail
        if check and unhealthy(response.status_code):
            error(response, error_message('patch', url), *args)

        return response
