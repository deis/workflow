import os

# security keys and auth tokens
SECRET_KEY = '{{ getv "/deis/controller/secretKey" }}'
BUILDER_KEY = '{{ getv "/deis/controller/builderKey" }}'

# scheduler settings
SCHEDULER_MODULE = 'scheduler'
SCHEDULER_URL = "https://{}:{}".format(
    os.environ.get('KUBERNETES_SERVICE_HOST', 'kubernetes.default.svc.cluster.local'),
    os.environ.get('KUBERNETES_SERVICE_PORT', '443'))

{{ if exists "/deis/controller/registrationMode" }}
REGISTRATION_MODE = '{{ getv "/deis/controller/registrationMode" }}'
{{ end }}

{{ if exists "/deis/controller/subdomain" }}
DEIS_RESERVED_NAMES = ['{{ getv "/deis/controller/subdomain" }}']
{{ end }}
