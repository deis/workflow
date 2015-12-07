import string
import json
import time

from .base import Base
from .client import error, unhealthy


class Pod(Base):
    TEMPLATE = """\
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

    def create(self, name, image, template=None):
        app_name = name.split('_')[0]
        name = name.replace('.', '-').replace('_', '-')

        # In case a whole template object is passed down
        if not template:
            template = json.loads(string.Template(self.TEMPLATE).substitute({
                'id': name,
                'version': self.api.version,
                'image': self.registry + '/' + image,
            }))

        create = self.api.post("/namespaces/{}/pods", app_name, json=template)

        # Wait for 5 seconds until pod is ready
        for _ in xrange(5):
            response = self.get(name, app_name, check=False)
            if unhealthy(response.status_code):
                time.sleep(1)
                continue

            break

        if unhealthy(response.status_code):
            error(create, 'create Pod in Namespace "{}"', app_name)

        return response

    def run(self, name, image, entrypoint, command):
        """run a one off command that creates a pod and then tears it down"""
        if command.startswith('-c '):
            args = command.split(' ', 1)
            args[1] = args[1][1:-1]
        else:
            args = [command[1:-1]]

        template = json.loads(string.Template(self.TEMPLATE).substitute({
            'id': name,
            'version': self.api.version,
            'image': self.registry + '/' + image,
        }))

        template['spec']['containers'][0]['command'] = [entrypoint]
        template['spec']['containers'][0]['args'] = args

        response = self.create(name, image, template)

        # Wait until pod is in the correct state
        app_name = name.split('_')[0]
        item = response.json()
        while(1):
            if item['status']['phase'] == 'Succeeded':
                response = self.log(name, app_name)
                self.delete(name, app_name)
                return 0, response.text
            elif item['status']['phase'] == 'Failed':
                pod_state = item['status']['containerStatuses'][0]['state']
                err_code = pod_state['terminated']['exitCode']
                self.delete(name, app_name)
                return err_code, response.text

            time.sleep(1)

        return 0, response.text

    def get(self, name, namespace, check=True):
        return self.api.get('/namespaces/{}/pods/{}', namespace, name, check=check)

    def status(self, name, namespace):
        """Returns the status code of a pod"""
        return self.get(name, namespace, check=False).status_code

    def all(self, namespace):
        return self.api.get('/namespaces/{}/pods', namespace)

    def delete(self, name, namespace):
        delete = self.api.delete('/namespaces/{}/pods/{}', namespace, name)

        # Verify the pod has been deleted. Give it 5 seconds.
        for _ in xrange(5):
            # Fetching without health check to check for 404
            status = self.status(name, namespace)
            if status == 404:
                break

            time.sleep(1)

        # Pod was not deleted within the grace period.
        if status != 404:
            error(delete, 'delete Pod "{}" in Namespace "{}"', name, namespace)

    def log(self, name, namespace):
        return self.api.get("/namespaces/{}/pods/{}/log", namespace, name)
