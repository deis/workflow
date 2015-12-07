from django.conf import settings
from .client import KubeHTTPClient


class Base(object):
    def __init__(self):
        self.registry = settings.REGISTRY_URL
        self.api = KubeHTTPClient(settings.SCHEDULER_URL)
