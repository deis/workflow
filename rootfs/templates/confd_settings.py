import os

# security keys and auth tokens
with open('/var/run/secrets/api/builder/auth/builder-key') as f:
    BUILDER_KEY = f.read().strip()

with open('/var/run/secrets/api/django/secret-key') as f:
    SECRET_KEY = f.read().strip()

with open('/var/run/secrets/deis/database/creds/user') as f:
    DATABASES['default']['USER'] = f.read().strip()

with open('/var/run/secrets/deis/database/creds/password') as f:
    DATABASES['default']['PASSWORD'] = f.read().strip()

# scheduler settings
SCHEDULER_MODULE = 'scheduler'
SCHEDULER_URL = "https://{}:{}".format(
    os.environ.get('KUBERNETES_SERVICE_HOST', 'kubernetes.default.svc.cluster.local'),
    os.environ.get('KUBERNETES_SERVICE_PORT', '443')
)

{{ if exists "/deis/controller/registrationMode" }}
REGISTRATION_MODE = '{{ getv "/deis/controller/registrationMode" }}'
{{ else }}
REGISTRATION_MODE = 'enabled'
{{ end }}

{{ if exists "/deis/controller/subdomain" }}
DEIS_RESERVED_NAMES = ['{{ getv "/deis/controller/subdomain" }}']
{{ end }}
