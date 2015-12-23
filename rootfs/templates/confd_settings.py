import os

# security keys and auth tokens
SECRET_KEY = '{{ getv "/deis/controller/secretKey" }}'
BUILDER_KEY = '{{ getv "/deis/controller/builderKey" }}'

# scheduler settings
SCHEDULER_MODULE = 'scheduler.k8s'
SCHEDULER_URL = "https://{}:{}".format(
    os.environ.get('KUBERNETES_SERVICE_HOST', 'kubernetes.default.svc.cluster.local'),
    os.environ.get('KUBERNETES_SERVICE_PORT', '443'))

# platform domain must be provided
DEIS_DOMAIN = '{{ getv "/deis/platform/domain" }}'

{{ if exists "/deis/controller/registrationMode" }}
REGISTRATION_MODE = '{{ getv "/deis/controller/registrationMode" }}'
{{ end }}

{{ if exists "/deis/controller/subdomain" }}
DEIS_RESERVED_NAMES = ['{{ getv "/deis/controller/subdomain" }}']
{{ end }}

# AUTH
# LDAP
{{ if exists "/deis/controller/auth/ldap/endpoint" }}
LDAP_ENDPOINT = '{{ if exists "/deis/controller/auth/ldap/endpoint" }}{{ getv "/deis/controller/auth/ldap/endpoint"}}{{ else }} {{ end }}'
BIND_DN = '{{ if exists "/deis/controller/auth/ldap/bind/dn" }}{{ getv "/deis/controller/auth/ldap/bind/dn"}}{{ else }} {{ end }}'
BIND_PASSWORD = '{{ if exists "/deis/controller/auth/ldap/bind/password" }}{{ getv "/deis/controller/auth/ldap/bind/password"}}{{ else }} {{ end }}'
USER_BASEDN = '{{ if exists "/deis/controller/auth/ldap/user/basedn" }}{{ getv "/deis/controller/auth/ldap/user/basedn"}}{{ else }} {{ end }}'
USER_FILTER = '{{ if exists "/deis/controller/auth/ldap/user/filter" }}{{ getv "/deis/controller/auth/ldap/user/filter"}}{{ else }} {{ end }}'
GROUP_BASEDN = '{{ if exists "/deis/controller/auth/ldap/group/basedn" }}{{ getv "/deis/controller/auth/ldap/group/basedn"}}{{ else }} {{ end }}'
GROUP_FILTER = '{{ if exists "/deis/controller/auth/ldap/group/filter" }}{{ getv "/deis/controller/auth/ldap/group/filter"}}{{ else }} {{ end }}'
GROUP_TYPE = '{{ if exists "/deis/controller/auth/ldap/group/type" }}{{ getv "/deis/controller/auth/ldap/group/type"}}{{ else }} {{ end }}'
{{ end }}
