import logging

from .states import JobState
from .abstract import AbstractSchedulerClient
from .client import unhealthy
from .replicationcontroller import ReplicationController
from .pod import Pod
from .service import Service
from .namespace import Namespace

log = logging.getLogger(__name__)


class KubeSchedulerClient(AbstractSchedulerClient):
    def deploy(self, name, image, command, **kwargs):
        log.debug('deploy %s, img %s, params %s, cmd "%s"', name, image, kwargs, command)
        app_name = kwargs.get('aname', {})
        app_type = name.split('.')[1]

        controller = ReplicationController()
        old_rc = controller.old(app_name, app_type)
        new_rc = controller.create(name, image, command, **kwargs)
        if old_rc:
            desired = int(old_rc['spec']['replicas'])
            old_rc_name = old_rc['metadata']['name']
        else:
            desired = 1

        new_rc_name = new_rc['metadata']['name']
        try:
            count = 1
            while desired >= count:
                new_rc = controller.scale(new_rc_name, count, app_name)
                if old_rc:
                    old_rc = controller.scale(old_rc_name, desired-count, app_name)
                count += 1
        except Exception as e:
            controller.scale(new_rc['metadata']['name'], 0, app_name)
            controller.delete(new_rc['metadata']['name'], app_name)
            if old_rc:
                controller.scale(old_rc['metadata']['name'], desired, app_name)

            raise RuntimeError('{} (deploy): {}'.format(name, e))

        if old_rc:
            controller.delete(old_rc_name, app_name)

    def scale(self, name, image, command, **kwargs):
        log.debug('scale %s, img %s, params %s, cmd "%s"', name, image, kwargs, command)
        app_name = kwargs.get('aname', {})
        rc_name = name.replace('.', '-').replace('_', '-')

        controller = ReplicationController()
        # Create if ReplicationController doesn't exist
        if unhealthy(controller.status(rc_name, app_name)):
            self.create(name, image, command, **kwargs)
            return

        name = name.replace('.', '-').replace('_', '-')
        num = kwargs.get('num', {})
        old_replicas = controller.get(name, app_name).json()['spec']['replicas']
        try:
            controller.scale(name, num, app_name)
        except Exception as e:
            controller.scale(name, old_replicas, app_name)
            raise RuntimeError('{} (Scale): {}'.format(name, e))

    def create(self, name, image, command, **kwargs):
        """Create a container."""
        log.debug('create %s, img %s, params %s, cmd "%s"', name, image, kwargs, command)
        controller = ReplicationController()
        controller.create(name, image, command, **kwargs)
        app_type = name.split('.')[1]
        name = name.replace('.', '-').replace('_', '-')
        app_name = kwargs.get('aname', {})
        try:
            Service().create(name, app_name, app_type)
        except:
            controller.scale(name, 0, app_name)
            controller.delete(name, app_name)
            raise

    def start(self, name):
        """Start a container."""
        pass

    def stop(self, name):
        """Stop a container."""
        pass

    def destroy(self, name):
        """Destroy a application by deleting its namespace."""
        log.debug('destroy %s', name)
        namespace = Namespace()
        response = namespace.get(name, check=False)
        if response.status_code == 404:
            log.warn('delete Namespace "%s": not found', name)
        else:
            namespace.delete(name)

    def logs(self, name):
        """Aggregate logs from all pods in the namespace"""
        log.debug("logs %s", name)
        app_name = name.split('_')[0]
        name = name.replace('.', '-').replace('_', '-')

        pod = Pod()
        items = pod.all(app_name).json()['items']
        log_data = ''
        for data in items:
            if name in data['metadata']['generateName'] and data['status']['phase'] == 'Running':
                log_data += pod.log(pod['metadata']['name'], app_name).text

        return log_data

    def run(self, name, image, entrypoint, command):
        """Run a one-off command."""
        log.debug('run %s, img %s, entypoint %s, cmd "%s"', name, image, entrypoint, command)
        return Pod().run(name, image, entrypoint, command)

    def state(self, name):
        """Display the state of a container."""
        # See "Pod Phase" at http://kubernetes.io/v1.1/docs/user-guide/pod-states.html
        phase_states = {
            'Pending': JobState.initialized,
            'Running': JobState.up,
            'Succeeded': JobState.down,
            'Failed': JobState.crashed,
            'Unknown': JobState.error,
        }

        try:
            app_name = name.split('_')[0]
            name = name.split('.')
            name = name[0] + '-' + name[1]
            name = name.replace('_', '-')

            items = Pod().all(app_name).json()['items']
            for data in items:
                if data['metadata']['generateName'] == name + '-':
                    phase = data['status']['phase']
                    return phase_states[phase]

            return JobState.destroyed
        except Exception as err:
            log.warn(err)
            return JobState.error

SchedulerClient = KubeSchedulerClient
