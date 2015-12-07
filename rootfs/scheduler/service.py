import json
import string
import time

from docker import Client
from .base import Base
from .pod import Pod
from .client import error, unhealthy


class Service(Base):
    TEMPLATE = """\
{
  "kind": "Service",
  "apiVersion": "$version",
  "metadata": {
    "name": "$name",
    "labels": {
      "app": "$label"
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

    def create(self, name, app_name, app_type):
        actual_pod = {}
        pod = Pod()
        for _ in xrange(300):
            items = pod.all(app_name).json()['items']
            for data in items:
                if (
                    'generateName' in data['metadata'] and
                    data['metadata']['generateName'] == name + '-'
                ):
                    actual_pod = data
                    break

            if actual_pod and actual_pod['status']['phase'] == 'Running':
                break

            time.sleep(1)

        container_id = actual_pod['status']['containerStatuses'][0]['containerID'].split("//")[1]
        # ip = actual_pod['status']['hostIP']
        # TODO: more robust way of determining the first exposed port--this will only work on
        # the node where this deis/workflow pod is running.
        # Find the first exposed port by inspecting the Docker container
        try:
            docker_cli = Client(version="auto")
            container = docker_cli.inspect_container(container_id)
            port = int(container['Config']['ExposedPorts'].keys()[0].split("/")[0])
        except:
            port = 5000

        template = json.loads(string.Template(self.TEMPLATE).substitute({
            'version': self.api.version,
            'port': port,
            'type': app_type,
            'name': app_name,
        }))

        resp = self.api.post('/namespaces/{}/services', app_name, check=False, json=template)
        if resp.status_code == 409:
            srv = self.get(app_name, app_name).json()
            if srv['spec']['selector']['type'] == 'web':
                return

            srv['spec']['selector']['type'] = app_type
            srv['spec']['ports'][0]['targetPort'] = port
            self.update(app_name, app_name, srv)
        elif unhealthy(resp.status_code):
            error(resp, 'create Service "{}" in Namespace "{}"', app_name, app_name)

    def delete(self, name, namespace):
        return self.api.delete("/namespaces/{}/services/{}", namespace, name)

    def update(self, name, namespace, data):
        return self.api.put('/namespaces/{}/services/{}', namespace, name, json=data)

    def get(self, name, namespace):
        return self.api.get("/namespaces/{}/services/{}", namespace, name)
