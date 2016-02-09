import json
import requests
import base64

from .abstract import AbstractSchedulerClient
from .states import JobState, TransitionError


# HACK: MockSchedulerClient is not persistent across requests
jobs = {}
secrets = {}


class MockSchedulerClient(AbstractSchedulerClient):

    def create(self, name, image, command, **kwargs):
        """Create a new container."""
        jobs.setdefault(name, {})['state'] = JobState.created

    def destroy(self, name):
        """Destroy a container."""
        jobs.setdefault(name, {})['state'] = JobState.destroyed

    def run(self, name, image, entrypoint, command):
        """Run a one-off command."""
        # dump input into a json object for testing purposes
        return 0, json.dumps({
            'name': name,
            'image': image,
            'entrypoint': entrypoint,
            'command': command,
        })

    def start(self, name):
        """Start a container."""
        if self.state(name) not in [JobState.created,
                                    JobState.up,
                                    JobState.down,
                                    JobState.crashed,
                                    JobState.error]:
            raise TransitionError(self.state(name),
                                  JobState.up,
                                  'the container must be stopped or up to start')
        jobs.setdefault(name, {})['state'] = JobState.up

    def state(self, name):
        """Display the given job's running state."""
        return jobs.get(name, {}).get('state', JobState.initialized)

    def stop(self, name):
        """Stop a container."""
        job = jobs.get(name, {})
        if job.get('state') not in [JobState.up, JobState.crashed, JobState.error]:
            raise TransitionError(job.get('state'),
                                  JobState.up,
                                  'the container must be up to stop')
        job['state'] = JobState.down

    # Related to k8s services
    def _get_service(self, namespace, name):
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b'{}'
        return resp

    def _update_service(self, namespace, name, data):
        pass

    def _get_nodes(self, **kwargs):
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b'{"items": [{"metadata": {"labels": {"env": "prod"}}}]}'
        return resp

    def _get_secret(self, namespace, name):
        # Fake out the secrets
        resp = requests.Response()
        resp.status_code = 200
        resp._content = json.dumps(secrets.get(name, {})).encode('UTF-8')
        return resp

    def _create_secret(self, namespace, name, data):
        items = {
            'data': {}
        }

        for key, item in data.items():
            items['data'][key] = base64.b64encode(bytes(item, 'UTF-8')).decode()

        secrets.setdefault(name, items)

    def _delete_secret(self, namespace, name):
        if name in secrets:
            secrets.pop(name)


SchedulerClient = MockSchedulerClient
