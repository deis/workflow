from .base import Base


class Namespace(Base):
    def create(self, name):
        data = {
            'kind': 'Namespace',
            'apiVersion': self.api.version,
            'metadata': {
                'name': name
            }
        }

        return self.api.post('/namespaces', name, json=data)

    def delete(self, name):
        namespace = name.split('_')[0]
        return self.api.delete('/namespaces/{}', namespace, check=False)

    def get(self, name, check=True):
        return self.api.get('/namespaces/{}', name, check=check)
