
class AbstractSchedulerClient(object):
    """
    A generic interface to a scheduler backend.
    """

    def create(self, name, image, command, **kwargs):
        """Create a new container."""
        raise NotImplementedError

    def destroy(self, name):
        """Destroy a container."""
        raise NotImplementedError

    def run(self, name, image, entrypoint, command):
        """Run a one-off command."""
        raise NotImplementedError

    def start(self, name):
        """Start a container."""
        raise NotImplementedError

    def state(self, name):
        """Display the given job's running state."""
        raise NotImplementedError

    def stop(self, name):
        """Stop a container."""
        raise NotImplementedError
