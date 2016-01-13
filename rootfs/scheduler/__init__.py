import json
import logging
import re
import string
import time
from urllib.parse import urljoin
import base64

from django.conf import settings
from docker import Client
from .states import JobState
from .abstract import AbstractSchedulerClient
import requests
from .utils import dict_merge


logger = logging.getLogger(__name__)

# Used for one off command runs on pods
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

RCD_TEMPLATE = """\
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
            "image": "$image",
            "env": [
            {
                "name":"DEIS_APP",
                "value":"$id"
            },
            {
                "name":"DEIS_RELEASE",
                "value":"$appversion"
            }
            ]
          }
        ]
      }
    }
  }
}
"""

RCB_TEMPLATE = """\
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
            "image": "quay.io/deisci/slugrunner:v2-beta",
            "imagePullPolicy": "Always",
            "env": [
            {
                "name":"PORT",
                "value":"5000"
            },
            {
                "name":"SLUG_URL",
                "value":"$image"
            },
            {
                "name":"DEBUG",
                "value":"1"
            },
            {
                "name":"DEIS_APP",
                "value":"$id"
            },
            {
                "name":"DEIS_RELEASE",
                "value":"$appversion"
            },
            {
                "name": "DOCKERIMAGE",
                "value":"1"
            }
            ],
            "volumeMounts":[
            {
                "name":"minio-user",
                "mountPath":"/var/run/secrets/object/store",
                "readOnly":true
            }
            ]
          }
        ],
        "volumes":[
        {
            "name":"minio-user",
            "secret":{
            "secretName":"minio-user"
            }
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
    },
    "annotations": {}
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

SECRET_TEMPLATE = """\
{
  "kind": "Secret",
  "apiVersion": "$version",
  "metadata": {
    "name": "minio-user",
    "namespace": "$id"
  },
  "type": "Opaque",
  "data":{
  "access-key-id": "$secretId",
  "access-secret-key": "$secretKey"
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

    def deploy(self, name, image, command, **kwargs):
        logger.debug('deploy {}, img {}, params {}, cmd "{}"'.format(name, image, kwargs, command))
        app_name = kwargs.get('aname', {})
        name = name.replace('.', '-').replace('_', '-')
        app_type = name.split('-')[-1]

        # Fetch old RC and create the new one for a release
        old_rc = self._get_old_rc(app_name, app_type)
        new_rc = self._create_rc(name, image, command, **kwargs)

        # Get the desired number to scale to
        if old_rc:
            desired = int(old_rc["spec"]["replicas"])
        else:
            desired = 1

        try:
            count = 1
            while desired >= count:
                logger.debug('scaling release {} to {} out of final {}'.format(
                    new_rc["metadata"]["name"], count, desired)
                )
                self._scale_rc(new_rc["metadata"]["name"], app_name, count)
                if old_rc:
                    logger.debug('scaling old release {} from {} to {}'.format(
                        old_rc["metadata"]["name"], desired, (desired-count))
                    )
                    self._scale_rc(old_rc["metadata"]["name"], app_name, (desired-count))

                count += 1
        except Exception as e:
            logger.error('Could not scale {} to {}. Deleting and going back to old release'.format(
                new_rc["metadata"]["name"], desired)
            )
            self._scale_rc(new_rc["metadata"]["name"], app_name, 0)
            self._delete_rc(new_rc["metadata"]["name"], app_name)
            if old_rc:
                self._scale_rc(old_rc["metadata"]["name"], app_name, desired)

            raise RuntimeError('{} (deploy): {}'.format(name, e))

        if old_rc:
            self._delete_rc(app_name, old_rc["metadata"]["name"])

    def scale(self, name, image, command, **kwargs):
        logger.debug('scale {}, img {}, params {}, cmd "{}"'.format(name, image, kwargs, command))
        app_name = kwargs.get('aname', {})
        rc_name = name.replace('.', '-').replace('_', '-')
        if unhealthy(self._get_rc_status(rc_name, app_name)):
            self.create(name, image, command, **kwargs)
            return

        name = name.replace('.', '-').replace('_', '-')
        num = kwargs.get('num', {})
        js_template = self._get_rc(name, app_name)
        old_replicas = js_template["spec"]["replicas"]
        try:
            self._scale_rc(name, app_name, num)
        except Exception as e:
            self._scale_rc(name, app_name, old_replicas)
            raise RuntimeError('{} (Scale): {}'.format(name, e))

    def create(self, name, image, command, **kwargs):
        """Create a container."""
        logger.debug('create {}, img {}, params {}, cmd "{}"'.format(name, image, kwargs, command))
        name = name.replace('.', '-').replace('_', '-')
        app_type = name.split('-')[-1]
        app_name = kwargs.get('aname', {})
        try:
            # Make sure the router knows what to do with this
            data = {}
            # TODO this should potentially be higher up in the flow
            # see http://docs.deis.io/en/latest/using_deis/process-types/#web-vs-cmd-process-types
            if app_type in ['web', 'cmd']:
                data = {'metadata': {'labels': {'routable': 'true'}}}
            self._create_namespace(app_name)
            self._create_secret(app_name)
            self._create_rc(name, image, command, **kwargs)
            self._create_service(name, app_name, app_type, data, image=image)

        except Exception as e:
            logger.debug(e)
            self._scale_rc(name, app_name, 0)
            self._delete_rc(name, app_name)
            raise

    def start(self, name):
        """Start a container."""
        pass

    def stop(self, name):
        """Stop a container."""
        pass

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
            for _ in range(5):
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

    def _api(self, tmpl, *args):
        """Return a fully-qualified Kubernetes API URL from a string template with args."""
        url = "/api/{}".format(self.apiversion) + tmpl.format(*args)
        return urljoin(self.url, url)

    # EVENTS #

    def _get_events(self, namespace):
        url = self._api("/namespaces/{}/events", namespace)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, "get Events in Namespace {}", namespace)

        return resp.status_code, resp.text, resp.reason

    # NAMESPACE #

    def _create_namespace(self, app_name):
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

    def _check_status(self, resp, app_name):
        if resp.status_code == 404:
            self._create_namespace(app_name)
        elif resp.status_code != 200:
            error(resp, "locate Namespace {}".format(app_name))

    # REPLICATION CONTROLLER #

    def _get_old_rc(self, name, app_type):
        url = self._api("/namespaces/{}/replicationcontrollers", name)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, 'get ReplicationControllers in Namespace "{}"', name)

        exists = False
        prev_rc = []
        for rc in resp.json()['items']:
            if('app' in rc['spec']['selector'] and name == rc['metadata']['labels']['app'] and
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

    def _get_rc(self, name, namespace):
        url = self._api("/namespaces/{}/replicationcontrollers/{}", namespace, name)
        resp = self.session.get(url)
        if unhealthy(resp.status_code):
            error(resp, 'get ReplicationController "{}" in Namespace "{}"', name, namespace)

        return resp.json()

    def _get_schedule_status(self, name, num, namespace):
        pods = []
        for _ in range(120):
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

        for _ in range(120):
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

    def _scale_rc(self, name, namespace, num):
        rc = self._get_rc(name, namespace)
        rc["spec"]["replicas"] = num

        url = self._api("/namespaces/{}/replicationcontrollers/{}", namespace, name)
        resp = self.session.put(url, json=rc)
        if unhealthy(resp.status_code):
            error(resp, 'scale ReplicationController "{}"', name)

        resource_ver = rc['metadata']['resourceVersion']
        for _ in range(30):
            js_template = self._get_rc(name, namespace)
            if js_template["metadata"]["resourceVersion"] != resource_ver:
                break

            time.sleep(1)

        self._get_schedule_status(name, num, namespace)
        for _ in range(120):
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

    def _create_rc(self, name, image, command, **kwargs):  # noqa
        container_fullname = name
        app_name = kwargs.get('aname', {})
        app_type = name.split('-')[-1]
        container_name = app_name + '-' + app_type
        args = command.split()
        num = kwargs.get('num', {})
        imgurl = self.registry + "/" + image
        TEMPLATE = RCD_TEMPLATE

        # Check if it is a slug builder image.
        # Example format: golden-earrings:git-5450cbcdaaf9afe6fadd219c94ac9c449bd62413s
        if kwargs.get('build_type', {}) == "buildpack":
            imgurl = 'http://{}/git/home/{}/push/slug.tgz'.format(
                settings.S3EP,
                image)
            TEMPLATE = RCB_TEMPLATE

        l = {
            "name": name,
            "id": app_name,
            "appversion": kwargs.get("version", {}),
            "version": self.apiversion,
            "image": imgurl,
            "num": kwargs.get("num", {}),
            "containername": container_name,
            "type": app_type,
        }
        template = string.Template(TEMPLATE).substitute(l)
        js_template = json.loads(template)
        containers = js_template["spec"]["template"]["spec"]["containers"]
        containers[0]['args'] = args
        loc = locals().copy()
        loc.update(re.match(MATCH, container_fullname).groupdict())
        mem = kwargs.get('memory', {}).get(app_type)
        cpu = kwargs.get('cpu', {}).get(app_type)
        env = kwargs.get('envs', {})
        if env:
            for k, v in env.items():
                containers[0]["env"].append({"name": k, "value": v})
        if mem or cpu:
            containers[0]["resources"] = {"limits": {}}

        if mem:
            if mem[-2:-1].isalpha() and mem[-1].isalpha():
                mem = mem[:-1]

            mem = mem+"i"
            containers[0]["resources"]["limits"]["memory"] = mem

        if cpu:
            containers[0]["resources"]["limits"]["cpu"] = cpu

        # add in healtchecks
        js_template = self._healthcheck(js_template, **kwargs['healthcheck'])

        url = self._api("/namespaces/{}/replicationcontrollers", app_name)
        resp = self.session.post(url, json=js_template)
        if unhealthy(resp.status_code):
            error(resp, 'create ReplicationController "{}" in Namespace "{}"',
                  name, app_name)
        create = False
        for _ in range(30):
            if not create and self._get_rc_status(name, app_name) == 404:
                time.sleep(1)
                continue
            create = True
            rc = self._get_rc(name, app_name)
            if (
                "observedGeneration" in rc["status"] and
                rc["metadata"]["generation"] == rc["status"]["observedGeneration"]
            ):
                break

            time.sleep(1)
        return resp.json()

    def _update_rc(self, namespace, app, data):
        url = self._api("/namespaces/{}/replicationcontrollers/{}", namespace, app)
        return self.session.put(url, json=data)

    def _delete_rc(self, namespace, name):
        url = self._api("/namespaces/{}/replicationcontrollers/{}", namespace, name)
        resp = self.session.delete(url)
        if unhealthy(resp.status_code):
            error(resp, 'delete ReplicationController "{}" in Namespace "{}"',
                  name, namespace)

    def _healthcheck(self, controller, path='/', port=8080, delay=30, timeout=1):
        # FIXME this logic ideally should live higher up
        if controller['spec']['selector']['type'] not in ['web', 'cmd']:
            return controller

        # Inspect if a PORT env is already defined, make sure that's the port used
        for item in controller['spec']['template']['spec']['containers'][0]['env']:
            if item['name'] == 'PORT':
                port = int(item['value'])

        # Only support HTTP checks for now
        # http://kubernetes.io/v1.1/docs/user-guide/pod-states.html#container-probes
        healthcheck = {
            # defines the health checking
            'livenessProbe': {
                # an http probe
                'httpGet': {
                    'path': path,
                    'port': port
                },
                # length of time to wait for a pod to initialize
                # after pod startup, before applying health checking
                'initialDelaySeconds': delay,
                'timeoutSeconds': timeout
            },
            'readinessProbe': {
                # an http probe
                'httpGet': {
                    'path': path,
                    'port': port
                },
                # length of time to wait for a pod to initialize
                # after pod startup, before applying health checking
                'initialDelaySeconds': delay,
                'timeoutSeconds': timeout
            },
        }

        # Because it comes from a JSON template, need to hit the first key
        controller['spec']['template']['spec']['containers'][0].update(healthcheck)

        return controller

    # SECRETS #

    def _create_secret(self, namespace):
        with open("/var/run/secrets/deis/minio/user/access-key-id", "rb") as the_file:
            secretId = the_file.read()
        with open("/var/run/secrets/deis/minio/user/access-secret-key", "rb") as the_file:
            secretKey = the_file.read()

        template = json.loads(string.Template(SECRET_TEMPLATE).substitute({
            "version": self.apiversion,
            "id": namespace,
            "secretId": base64.b64encode(secretId).decode(),
            "secretKey": base64.b64encode(secretKey).decode(),
        }))

        url = self._api("/namespaces/{}/secrets", namespace)
        resp = self.session.post(url, json=template)
        if unhealthy(resp.status_code):
            error(resp, 'failed to create secret in Namespace "{}"', namespace)

    # SERVICES #

    def _get_service(self, name, namespace):
        url = self._api("/namespaces/{}/services/{}", namespace, name)
        response = self.session.get(url)
        if unhealthy(response.status_code):
            error(response, 'get Service "{}" in Namespace "{}"', name, namespace)

        return response

    def _create_service(self, name, app_name, app_type, data={}, **kwargs):
        docker_cli = Client(version="auto")
        image = kwargs.get('image')
        try:
            image = self.registry + '/' + image
            # image already includes the tag, so we split it out here
            docker_cli.pull(image.rsplit(':')[0], image.rsplit(':')[1])
            image_info = docker_cli.inspect_image(image)
            port = int(list(image_info['Config']['ExposedPorts'].keys())[0].split("/")[0])
        except:
            port = 5000
        l = {
            "version": self.apiversion,
            "port": port,
            "type": app_type,
            "name": app_name,
        }
        # Merge external data on to the prefined template
        template = json.loads(string.Template(SERVICE_TEMPLATE).substitute(l))
        data = dict_merge(template, data)
        url = self._api("/namespaces/{}/services", app_name)
        resp = self.session.post(url, json=data)
        if resp.status_code == 409:
            srv = self._get_service(app_name, app_name).json()
            if srv['spec']['selector']['type'] == 'web':
                return
            srv['spec']['selector']['type'] = app_type
            srv['spec']['ports'][0]['targetPort'] = port
            resp2 = self._update_service(app_name, app_name, srv)
            if unhealthy(resp2.status_code):
                error(resp, 'update Service "{}" in Namespace "{}"', app_name, app_name)
        elif unhealthy(resp.status_code):
            error(resp, 'create Service "{}" in Namespace "{}"', app_name, app_name)

    def _update_service(self, namespace, app, data):
        url = self._api("/namespaces/{}/services/{}", namespace, app)
        return self.session.put(url, json=data)

    # PODS #

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
        for _ in range(5):
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

SchedulerClient = KubeHTTPClient
