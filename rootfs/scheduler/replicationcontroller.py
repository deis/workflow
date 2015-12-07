import re
import string
import json
import time

from .base import Base
from .pod import Pod
from .events import Events
from .namespace import Namespace


class ReplicationController(Base):
    TEMPLATE = """\
{
  "kind": "ReplicationController",
  "apiVersion": "$version",
  "metadata": {
    "name": "$label",
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

    def create(self, name, image, command, **kwargs):
        container_fullname = name
        app_name = kwargs.get('aname', {})
        app_type = name.split('.')[1]
        container_name = app_name + '-' + app_type
        name = name.replace('.', '-').replace('_', '-')
        args = command.split()

        # First check if a Namespace needs to be created
        namespace = Namespace()
        response = namespace.get(app_name, check=False)
        if response.status_code == 404:
            namespace.create(app_name)
        elif response.status_code != 200:
            # TODO can this be abstracted into the get method?
            errmsg = 'locate Namespace {}'.format(app_name)
            errmsg = "failed to {}: {} {}\n{}".format(
                errmsg,
                response.status_code,
                response.reason,
                response.text
            )
            raise RuntimeError(errmsg)

        num = kwargs.get('num', {})

        template = json.loads(string.Template(self.TEMPLATE).substitute({
            'name': name,
            'id': app_name,
            'appversion': kwargs.get('version', {}),
            'version': self.api.version,
            'image': self.registry + '/' + image,
            'num': kwargs.get('num', {}),
            'containername': container_name,
            'type': app_type,
        }))

        containers = template['spec']['template']['spec']['containers']
        containers[0]['args'] = args

        # Validate name
        match = re.compile(r'(?P<app>[a-z0-9-]+)_?(?P<version>v[0-9]+)?\.?(?P<c_type>[a-z-_]+)')
        loc = locals().copy()
        loc.update(re.match(match, container_fullname).groupdict())

        # CPU / Memory handling
        mem = kwargs.get('memory', {}).get(loc['c_type'])
        cpu = kwargs.get('cpu', {}).get(loc['c_type'])
        if mem or cpu:
            containers[0]['resources'] = {'limits': {}}

        if mem:
            if mem[-2:-1].isalpha() and mem[-1].isalpha():
                mem = mem[:-1]

            mem = mem + 'i'
            containers[0]['resources']['limits']['memory'] = mem

        if cpu:
            cpu = float(cpu)/1024
            containers[0]['resources']['limits']['cpu'] = cpu

        # Create Replication Controller
        url = '/namespaces/{}/replicationcontrollers'
        response = self.api.post(url, app_name, name, json=template)

        create = False
        for _ in xrange(30):
            if not create and self.status(name, app_name) == 404:
                time.sleep(1)
                continue

            create = True
            data = self.get(name, app_name)
            if (
                'observedGeneration' in data['status'] and
                data['metadata']['generation'] == data['status']['observedGeneration']
            ):
                break

            time.sleep(1)

        return response.json()

    def status(self, name, namespace):
        return self.get(name, namespace, check=False).status_code

    def get(self, name, namespace, check=True):
        url = "/namespaces/{}/replicationcontrollers/{}"
        return self.api.get(url, namespace, name, check=check)

    def all(self, name):
        return self.api.get("/namespaces/{}/replicationcontrollers", name)

    def old(self, name, app_type):
        exists = False
        prev_rc = []
        for data in self.all(name).json()['items']:
            if (
                'name' in data['metadata']['labels'] and
                name == data['metadata']['labels']['name'] and
                'type' in data['spec']['selector'] and
                app_type == data['spec']['selector']['type']
            ):
                exists = True
                prev_rc = data
                break

        if exists:
            return prev_rc

        return 0

    def delete(self, name, namespace):
        return self.api.delete("/namespaces/{}/replicationcontrollers/{}", namespace, name)

    def update(self, name, namespace, data):
        url = '/namespaces/{}/replicationcontrollers/{}'
        return self.api.put(url, namespace, name, json=data)

    def schedule_status(self, name, num, namespace):
        pods = []
        pod = Pod()
        for _ in xrange(120):
            count = 0
            pods = []
            items = pod.all(namespace).json()['items']
            for pod in items:
                if pod['metadata']['generateName'] == name+'-':
                    count += 1
                    pods.append(pod['metadata']['name'])

            if count == num:
                break

            time.sleep(1)

        events = Events()
        for _ in xrange(120):
            count = 0
            items = events.get(namespace).json()['items']
            for event in items:
                if (
                    event['involvedObject']['name'] in pods and
                    event['source']['component'] == 'scheduler'
                ):
                    if event['reason'] != 'Scheduled':
                        raise RuntimeError(event['message'])

                    count += 1

            if count == num:
                break

            time.sleep(1)

    def scale(self, name, num, namespace):
        # Get the current controller and change the number
        controller = self.get(name, namespace).json()
        controller['spec']['replicas'] = num
        self.update(name, namespace, controller)

        resource_version = controller['metadata']['resourceVersion']
        for _ in xrange(30):
            template = self.get(name, namespace).json()
            if template['metadata']['resourceVersion'] != resource_version:
                break

            time.sleep(1)

        self.schedule_status(name, num, namespace)
        pod = Pod()
        for _ in xrange(120):
            count = 0
            items = pod.all(namespace).json()['items']
            for item in items:
                if (
                    item['metadata']['generateName'] == name + '-' and
                    item['status']['phase'] == 'Running'
                ):
                    count += 1

            if count == num:
                break

            time.sleep(1)
