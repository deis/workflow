from .base import Base


class Events(Base):
    def get(self, namespace):
        return self.api.get('/namespaces/{}/events', namespace)
