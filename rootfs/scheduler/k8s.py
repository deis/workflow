import json
import logging
import re
import string
import time
import urlparse

from django.conf import settings
from docker import Client
from .states import JobState
from . import AbstractSchedulerClient
import requests

logger = logging.getLogger(__name__)


POD_TEMPLATE = """\
{
  "kind": "Pod",
  "apiVersion": "$version",
  "metadata": {
    "name": "$id"
  },
  "spec": {
    "containers": [
      {
        "name": "$id",
        "image": "$image"
      }
    ],
    "restartPolicy": "Never"
  }
}
"""

RC_TEMPLATE = """\
{
  "kind": "ReplicationController",
  "apiVersion": "$version",
  "metadata": {
    "name": "$name",
    "labels": {
      "app": "$id",
      "heritage": "deis"
    }
  },
  "spec": {
    "replicas": $num,
    "selector": {
      "app": "$id",
      "version": "$appversion",
      "type": "$type",
      "heritage": "deis"
    },
    "template": {
      "metadata": {
        "labels": {
          "app": "$id",
          "version": "$appversion",
          "type": "$type",
          "heritage": "deis"
        }
      },
      "spec": {
        "containers": [
          {
            "name": "$containername",
            "image": "$image"
          }
        ]
      }
    }
  }
}
"""

SERVICE_TEMPLATE = """\
{
  "kind": "Service",
  "apiVersion": "$version",
  "metadata": {
    "name": "$name",
    "labels": {
      "app": "$name"
    }
  },
  "spec": {
    "ports": [
      {
        "port": 80,
        "targetPort": $port,
        "protocol": "TCP"
      }
    ],
    "selector": {
      "app": "$name",
      "type": "$type",
      "heritage": "deis"
    }
  }
}
"""

MATCH = re.compile(
    r'(?P<app>[a-z0-9-]+)_?(?P<version>v[0-9]+)?\.?(?P<c_type>[a-z-_]+)')


def error(resp, errmsg, *args):
    errmsg = errmsg.format(*args)
    errmsg = "failed to {}: {} {}\n{}".format(errmsg, resp.status_code, resp.reason, resp.json())
    raise RuntimeError(errmsg)


def unhealthy(status_code):
    if not 200 <= status_code <= 299:
        return True

    return False


class KubeHTTPClient(AbstractSchedulerClient):

    def __init__(self, target, auth, options):
        super(KubeHTTPClient, self).__init__(target, auth, options)
        self.url = settings.SCHEDULER_URL
        self.registry = settings.REGISTRY_URL
        self.apiversion = "v1"
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as token_file:
            token = token_file.read()
        session = requests.Session()
        session.headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        }
        # TODO: accessing the k8s api server by IP address rather than hostname avoids
        # intermittent DNS errors, but at the price of disabling cert verification.
        # session.verify = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
        session.verify = False
        self.session = session

    def _api(self, tmpl, *args):
        """Return a fully-qualified Kubernetes API URL from a string template with args."""
        url = "/api/{}".format(self.apiversion) + tmpl.format(*args)
        return urlparse.urljoin(self.url, url)

    def _get_old_rc(self, name, app_type):
        url = self._api("/namespaces/{}/replicationcontrollers", name)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, 'get ReplicationControllers in Namespace "{}"', name)

        exists = False
        prev_rc = []
        for rc in resp.json()['items']:
            if('name' in rc['metadata']['labels'] and name == rc['metadata']['labels']['name'] and
               'type' in rc['spec']['selector'] and app_type == rc['spec']['selector']['type']):
                exists = True
                prev_rc = rc
                break
        if exists:
            return prev_rc

        return 0

    def _get_rc_status(self, name, namespace):
        url = self._api("/namespaces/{}/replicationcontrollers/{}", namespace, name)
        resp = self.session.get(url)
        return resp.status_code

    def _get_rc_(self, name, namespace):
        url = self._api("/namespaces/{}/replicationcontrollers/{}", namespace, name)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, 'get ReplicationController "{}" in Namespace "{}"', name, namespace)

        return resp.json()

    def deploy(self, name, image, command, **kwargs):
        logger.debug('deploy {}, img {}, params {}, cmd "{}"'.format(name, image, kwargs, command))
        app_name = kwargs.get('aname', {})
        app_type = name.split(".")[1]
        old_rc = self._get_old_rc(app_name, app_type)
        new_rc = self._create_rc(name, image, command, **kwargs)
        if old_rc:
            desired = int(old_rc["spec"]["replicas"])
            old_rc_name = old_rc["metadata"]["name"]
        else:
            desired = 1

        new_rc_name = new_rc["metadata"]["name"]
        try:
            count = 1
            while desired >= count:
                new_rc = self._scale_app(new_rc_name, count, app_name)
                if old_rc:
                    old_rc = self._scale_app(old_rc_name, desired-count, app_name)
                count += 1
        except Exception as e:
            self._scale_app(new_rc["metadata"]["name"], 0, app_name)
            self._delete_rc(new_rc["metadata"]["name"], app_name)
            if old_rc:
                self._scale_app(old_rc["metadata"]["name"], desired, app_name)

            raise RuntimeError('{} (deploy): {}'.format(name, e))
        if old_rc:
            self._delete_rc(old_rc_name, app_name)

    def _get_events(self, namespace):
        url = self._api("/namespaces/{}/events", namespace)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, "get Events in Namespace {}", namespace)

        return resp.status_code, resp.text, resp.reason

    def _get_schedule_status(self, name, num, namespace):
        pods = []
        for _ in xrange(120):
            count = 0
            pods = []
            status, data, reason = self._get_pods(namespace)
            parsed_json = json.loads(data)
            for pod in parsed_json['items']:
                if pod['metadata']['generateName'] == name+'-':
                    count += 1
                    pods.append(pod['metadata']['name'])

            if count == num:
                break

            time.sleep(1)

        for _ in xrange(120):
            count = 0
            status, data, reason = self._get_events(namespace)
            parsed_json = json.loads(data)
            for event in parsed_json['items']:
                if(event['involvedObject']['name'] in pods and
                   event['source']['component'] == 'scheduler'):
                    if event['reason'] == 'Scheduled':
                        count += 1
                    else:
                        raise RuntimeError(event['message'])

            if count == num:
                break

            time.sleep(1)

    def _scale_rc(self, rc, namespace):
        name = rc['metadata']['name']
        num = rc["spec"]["replicas"]
        url = self._api("/namespaces/{}/replicationcontrollers/{}", namespace, name)
        resp = self.session.put(url, json=rc)
        if unhealthy(resp.status_code):
            error(resp, 'scale ReplicationController "{}"', name)

        resource_ver = rc['metadata']['resourceVersion']
        for _ in xrange(30):
            js_template = self._get_rc_(name, namespace)
            if js_template["metadata"]["resourceVersion"] != resource_ver:
                break

            time.sleep(1)

        self._get_schedule_status(name, num, namespace)
        for _ in xrange(120):
            count = 0
            status, data, reason = self._get_pods(namespace)
            parsed_json = json.loads(data)
            for pod in parsed_json['items']:
                if(pod['metadata']['generateName'] == name+'-' and
                   pod['status']['phase'] == 'Running'):
                    count += 1

            if count == num:
                break

            time.sleep(1)

    def _scale_app(self, name, num, namespace):
        js_template = self._get_rc_(name, namespace)
        js_template["spec"]["replicas"] = num
        self._scale_rc(js_template, namespace)

    def scale(self, name, image, command, **kwargs):
        logger.debug('scale {}, img {}, params {}, cmd "{}"'.format(name, image, kwargs, command))
        app_name = kwargs.get('aname', {})
        rc_name = name.replace('.', '-').replace('_', '-')
        if unhealthy(self._get_rc_status(rc_name, app_name)):
            self.create(name, image, command, **kwargs)
            return

        name = name.replace('.', '-').replace('_', '-')
        num = kwargs.get('num', {})
        js_template = self._get_rc_(name, app_name)
        old_replicas = js_template["spec"]["replicas"]
        try:
            self._scale_app(name, num, app_name)
        except Exception as e:
            self._scale_app(name, old_replicas, app_name)
            raise RuntimeError('{} (Scale): {}'.format(name, e))

    def _create_rc(self, name, image, command, **kwargs):
        container_fullname = name
        app_name = kwargs.get('aname', {})
        app_type = name.split('.')[1]
        container_name = app_name + '-' + app_type
        name = name.replace('.', '-').replace('_', '-')
        args = command.split()

        # First ensure that the namespace was created
        url = self._api("/namespaces/{}", app_name)
        resp = self.session.get(url)
        if resp.status_code == 404:
            url = self._api("/namespaces")
            data = {
                "kind": "Namespace",
                "apiVersion": self.apiversion,
                "metadata": {
                    "name": app_name
                }
            }

            resp = self.session.post(url, json=data)
            if not resp.status_code == 201:
                error(resp, "create Namespace {}".format(app_name))
        elif resp.status_code != 200:
            error(resp, "locate Namespace {}".format(app_name))

        num = kwargs.get('num', {})
        l = {
            "name": name,
            "id": app_name,
            "appversion": kwargs.get("version", {}),
            "version": self.apiversion,
            "image": self.registry + "/" + image,
            "num": kwargs.get("num", {}),
            "containername": container_name,
            "type": app_type,
        }

        template = string.Template(RC_TEMPLATE).substitute(l)
        js_template = json.loads(template)
        containers = js_template["spec"]["template"]["spec"]["containers"]
        containers[0]['args'] = args
        loc = locals().copy()
        loc.update(re.match(MATCH, container_fullname).groupdict())
        mem = kwargs.get('memory', {}).get(loc['c_type'])
        cpu = kwargs.get('cpu', {}).get(loc['c_type'])
        if mem or cpu:
            containers[0]["resources"] = {"limits": {}}

        if mem:
            if mem[-2:-1].isalpha() and mem[-1].isalpha():
                mem = mem[:-1]

            mem = mem+"i"
            containers[0]["resources"]["limits"]["memory"] = mem

        if cpu:
            cpu = float(cpu)/1024
            containers[0]["resources"]["limits"]["cpu"] = cpu

        url = self._api("/namespaces/{}/replicationcontrollers", app_name)
        resp = self.session.post(url, json=js_template)
        if unhealthy(resp.status_code):
            error(resp, 'create ReplicationController "{}" in Namespace "{}"',
                  name, app_name)

        create = False
        for _ in xrange(30):
            if not create and self._get_rc_status(name, app_name) == 404:
                time.sleep(1)
                continue

            create = True
            rc = self._get_rc_(name, app_name)
            if ("observedGeneration" in rc["status"]
                    and rc["metadata"]["generation"] == rc["status"]["observedGeneration"]):
                break

            time.sleep(1)

        return resp.json()

    def create(self, name, image, command, **kwargs):
        """Create a container."""
        logger.debug('create {}, img {}, params {}, cmd "{}"'.format(name, image, kwargs, command))
        self._create_rc(name, image, command, **kwargs)
        app_type = name.split('.')[1]
        name = name.replace('.', '-').replace('_', '-')
        app_name = kwargs.get('aname', {})
        try:
            self._create_service(name, app_name, app_type)
        except:
            self._scale_app(name, 0, app_name)
            self._delete_rc(name, app_name)
            raise

    def _get_service(self, name, namespace):
        url = self._api("/namespaces/{}/services/{}", namespace, name)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, 'get Service "{}" in Namespace "{}"', name, namespace)

        return resp.status_code, resp.text, resp.reason

    def _create_service(self, name, app_name, app_type):
        actual_pod = {}
        for _ in xrange(300):
            status, data, reason = self._get_pods(app_name)
            parsed_json = json.loads(data)
            for pod in parsed_json['items']:
                if('generateName' in pod['metadata'] and
                   pod['metadata']['generateName'] == name + '-'):
                    actual_pod = pod
                    break

            if actual_pod and actual_pod['status']['phase'] == 'Running':
                break

            time.sleep(1)

        container_id = actual_pod['status']['containerStatuses'][0]['containerID'].split("//")[1]
        # ip = actual_pod['status']['hostIP']
        # TODO: more robust way of determining the first exposed port--this will only work on
        # the node where this deis/workflow pod is running.
        # Find the first exposed port by inspecting the Docker container
        docker_cli = Client(version="auto")
        try:
            container = docker_cli.inspect_container(container_id)
            port = int(container['Config']['ExposedPorts'].keys()[0].split("/")[0])
        except:
            port = 5000

        l = {
            "version": self.apiversion,
            "port": port,
            "type": app_type,
            "name": app_name,
        }

        template = string.Template(SERVICE_TEMPLATE).substitute(l)
        url = self._api("/namespaces/{}/services", app_name)
        resp = self.session.post(url, json=json.loads(template))
        if resp.status_code == 409:
            status, data, reason = self._get_service(app_name, app_name)
            srv = json.loads(data)
            if srv['spec']['selector']['type'] == 'web':
                return

            srv['spec']['selector']['type'] = app_type
            srv['spec']['ports'][0]['targetPort'] = port
            url = self._api("/namespaces/{}/services/{}", app_name, app_name)
            resp2 = self.session.put(url, json=srv)
            if unhealthy(resp2.status_code):
                error(resp, 'update Service "{}" in Namespace "{}"', app_name, app_name)
        elif unhealthy(resp.status_code):
            error(resp, 'create Service "{}" in Namespace "{}"', app_name, app_name)

    def start(self, name):
        """Start a container."""
        pass

    def stop(self, name):
        """Stop a container."""
        pass

    def _delete_rc(self, name, namespace):
        url = self._api("/namespaces/{}/replicationcontrollers/{}", namespace, name)
        resp = self.session.delete(url)
        if unhealthy(resp.status_code):
            error(resp, 'delete ReplicationController "{}" in Namespace "{}"',
                  name, namespace)

    def destroy(self, name):
        """Destroy a application by deleting its namespace."""
        namespace = name.split("_")[0]
        logger.debug("destroy {}".format(name))
        url = self._api("/namespaces/{}", namespace)
        resp = self.session.delete(url)
        if resp.status_code == 404:
            logger.warn('delete Namespace "{}": not found'.format(namespace))
        elif resp.status_code != 200:
            error(resp, 'delete Namespace "{}"', namespace)

    def _get_pod(self, name, namespace):
        url = self._api("/namespaces/{}/pods/{}", namespace, name)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, 'get Pod "{}" in Namespace "{}"', name, namespace)

        return resp.status_code, resp.reason, resp.text

    def _get_pods(self, namespace):
        url = self._api("/namespaces/{}/pods", namespace)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, 'get Pods in Namespace "{}"', namespace)

        return resp.status_code, resp.text, resp.reason

    def _delete_pod(self, name, namespace):
        url = self._api("/namespaces/{}/pods/{}", namespace, name)
        resp = self.session.delete(url)
        if unhealthy(resp.status_code):
            error(resp, 'delete Pod "{}" in Namespace "{}"', name, namespace)

        # Verify the pod has been deleted. Give it 5 seconds.
        for _ in xrange(5):
            status, reason, data = self._get_pod(name, namespace)
            if status == 404:
                break

            time.sleep(1)

        # Pod was not deleted within the grace period.
        if status != 404:
            error(resp, 'delete Pod "{}" in Namespace "{}"', name, namespace)

    def _pod_log(self, name, namespace):
        url = self._api("/namespaces/{}/pods/{}/log", namespace, name)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, 'get logs for Pod "{}" in Namespace "{}"', name, namespace)

        return resp.status_code, resp.text, resp.reason

    def logs(self, name):
        logger.debug("logs {}".format(name))
        app_name = name.split('_')[0]
        name = name.replace('.', '-').replace('_', '-')
        status, data, reason = self._get_pods(app_name)
        parsed_json = json.loads(data)
        log_data = ''
        for pod in parsed_json['items']:
            if name in pod['metadata']['generateName'] and pod['status']['phase'] == 'Running':
                status, data, reason = self._pod_log(pod['metadata']['name'], app_name)
                log_data += data

        return log_data

    def run(self, name, image, entrypoint, command):
        """Run a one-off command."""
        logger.debug('run {}, img {}, entypoint {}, cmd "{}"'.format(
            name, image, entrypoint, command))
        appname = name.split('_')[0]
        name = name.replace('.', '-').replace('_', '-')
        l = {
            'id': name,
            'version': self.apiversion,
            'image': self.registry + '/' + image,
        }

        template = string.Template(POD_TEMPLATE).substitute(l)
        if command.startswith('-c '):
            args = command.split(' ', 1)
            args[1] = args[1][1:-1]
        else:
            args = [command[1:-1]]

        js_template = json.loads(template)
        js_template['spec']['containers'][0]['command'] = [entrypoint]
        js_template['spec']['containers'][0]['args'] = args
        url = self._api("/namespaces/{}/pods", appname)
        resp = self.session.post(url, json=js_template)
        if unhealthy(resp.status_code):
            error(resp, 'create Pod in Namespace "{}"', appname)

        while(1):
            parsed_json = {}
            status = 404
            reason = ''
            data = ''
            for _ in xrange(5):
                status, reason, data = self._get_pod(name, appname)
                if unhealthy(status):
                    time.sleep(1)
                    continue

                parsed_json = json.loads(data)
                break

            if unhealthy(status):
                error(resp, 'create Pod in Namespace "{}"', appname)

            if parsed_json['status']['phase'] == 'Succeeded':
                status, data, reason = self._pod_log(name, appname)
                self._delete_pod(name, appname)
                return 0, data
            elif parsed_json['status']['phase'] == 'Failed':
                pod_state = parsed_json['status']['containerStatuses'][0]['state']
                err_code = pod_state['terminated']['exitCode']
                self._delete_pod(name, appname)
                return err_code, data

            time.sleep(1)

        return 0, data

    def state(self, name):
        """Display the state of a container."""
        # See "Pod Phase" at http://kubernetes.io/v1.1/docs/user-guide/pod-states.html
        phase_states = {
            "Pending": JobState.initialized,
            "Running": JobState.up,
            "Succeeded": JobState.down,
            "Failed": JobState.crashed,
            "Unknown": JobState.error,
        }

        try:
            appname = name.split('_')[0]
            name = name.split('.')
            name = name[0] + '-' + name[1]
            name = name.replace('_', '-')
            status, data, reason = self._get_pods(appname)
            parsed_json = json.loads(data)
            for pod in parsed_json["items"]:
                if pod["metadata"]["generateName"] == name + "-":
                    phase = pod["status"]["phase"]
                    return phase_states[phase]

            return JobState.destroyed
        except Exception as err:
            logger.warn(err)
            return JobState.error

SchedulerClient = KubeHTTPClient
