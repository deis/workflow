"""
Django settings for the Deis project.
"""

from __future__ import unicode_literals
import os.path
import random
import string
import sys
import tempfile


PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

DEBUG = False

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

CONN_MAX_AGE = 60 * 3

# SECURITY: change this to allowed fqdn's to prevent host poisioning attacks
# https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.abspath(os.path.join(__file__, '..', '..', 'static'))

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Manage templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages"
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'api.middleware.APIVersionMiddleware',
    'deis.middleware.PlatformVersionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'deis.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'deis.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    # Third-party apps
    'guardian',
    'jsonfield',
    'gunicorn',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # Deis apps
    'api'
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
)

ANONYMOUS_USER_ID = -1
LOGIN_URL = '/v2/auth/login/'
LOGIN_REDIRECT_URL = '/'

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = (
    'content-type',
    'accept',
    'origin',
    'Authorization',
    'Host',
)

CORS_EXPOSE_HEADERS = (
    'DEIS_API_VERSION',
    'DEIS_PLATFORM_VERSION',
    'Deis-Release',
)

# standard datetime format used for logging, model timestamps, etc.
DEIS_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%Z'

REST_FRAMEWORK = {
    'DATETIME_FORMAT': DEIS_DATETIME_FORMAT,
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.ModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# URLs that end with slashes are ugly
APPEND_SLASH = False

# Determine where to send syslog messages
if os.path.exists('/dev/log'):           # Linux rsyslog
    SYSLOG_ADDRESS = '/dev/log'
elif os.path.exists('/var/log/syslog'):  # Mac OS X syslog
    SYSLOG_ADDRESS = '/var/log/syslog'
else:                                    # default SysLogHandler address
    SYSLOG_ADDRESS = ('localhost', 514)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'rsyslog': {
            'class': 'logging.handlers.SysLogHandler',
            'address': SYSLOG_ADDRESS,
            'facility': 'local0',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'api': {
            'handlers': ['console', 'mail_admins', 'rsyslog'],
            'level': 'INFO',
            'propagate': True,
        },
        'registry': {
            'handlers': ['console', 'mail_admins', 'rsyslog'],
            'level': 'INFO',
            'propagate': True,
        },
        'scheduler': {
            'handlers': ['console', 'mail_admins', 'rsyslog'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
TEST_RUNNER = 'api.tests.SilentDjangoTestSuiteRunner'

# etcd settings
ETCD_HOST = os.environ.get('DEIS_ETCD_1_SERVICE_HOST', '127.0.0.1')
ETCD_PORT = os.environ.get('DEIS_ETCD_1_SERVICE_PORT_CLIENT', 4001)

# default deis settings
LOG_LINES = 1000
TEMPDIR = tempfile.mkdtemp(prefix='deis')

# names which apps cannot reserve for routing
DEIS_RESERVED_NAMES = ['deis']

# default scheduler settings
SCHEDULER_MODULE = 'scheduler.mock'
SCHEDULER_URL = 'localhost'
SCHEDULER_AUTH = None
SCHEDULER_OPTIONS = None

# security keys and auth tokens
SECRET_KEY = os.environ.get('DEIS_SECRET_KEY', 'CHANGEME_sapm$s%upvsw5l_zuy_&29rkywd^78ff(qi')
BUILDER_KEY = os.environ.get('DEIS_BUILDER_KEY', 'CHANGEME_sapm$s%upvsw5l_zuy_&29rkywd^78ff(qi')

# registry settings
REGISTRY_HOST = os.environ.get('DEIS_REGISTRY_SERVICE_HOST', '127.0.0.1')
REGISTRY_PORT = os.environ.get('DEIS_REGISTRY_SERVICE_PORT', 5000)
REGISTRY_URL = '{}:{}'.format(REGISTRY_HOST, REGISTRY_PORT)

BUILDER_HOST = os.environ.get('DEIS_BUILDER_SERVICE_HOST', '127.0.0.1')
MINIO_HOST = os.environ.get('DEIS_MINIO_SERVICE_HOST', BUILDER_HOST)
MINIO_PORT = os.environ.get('DEIS_MINIO_SERVICE_PORT', 3000)
S3EP_HOST = os.environ.get('DEIS_OUTSIDE_STORAGE_HOST', MINIO_HOST)
S3EP_PORT = os.environ.get('DEIS_OUTSIDE_STORAGE_PORT', MINIO_PORT)
S3EP = '{}:{}'.format(S3EP_HOST, S3EP_PORT)
# logger settings
LOGGER_HOST = os.environ.get('DEIS_LOGGER_SERVICE_HOST', '127.0.0.1')
LOGGER_PORT = os.environ.get('DEIS_LOGGER_SERVICE_PORT', 8088)

# check if we can register users with `deis register`
REGISTRATION_ENABLED = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DEIS_DATABASE_NAME', 'deis'),
        'USER': os.environ.get('DEIS_DATABASE_USER', ''),
        'PASSWORD': os.environ.get('DEIS_DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DEIS_DATABASE_SERVICE_HOST', ''),
        'PORT': os.environ.get('DEIS_DATABASE_SERVICE_PORT', 5432),
        # randomize test database name so we can run multiple unit tests simultaneously
        'TEST_NAME': "unittest-{}".format(''.join(
            random.choice(string.ascii_letters + string.digits) for _ in range(8)))
    }
}

APP_URL_REGEX = '[a-z0-9-]+'

# Honor HTTPS from a trusted proxy
# see https://docs.djangoproject.com/en/1.6/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Unit Hostname handling.
# Supports:
#  default      - Docker generated hostname
#  application  - Hostname based on application unit name (i.e. my-application.v2.web.1)
#  server       - Hostname based on CoreOS server hostname
UNIT_HOSTNAME = 'default'

# Create a file named "local_settings.py" to contain sensitive settings data
# such as database configuration, admin email, or passwords and keys. It
# should also be used for any settings which differ between development
# and production.
# The local_settings.py file should *not* be checked in to version control.
try:
    from .local_settings import *  # noqa
except ImportError:
    pass

# have confd_settings within container execution override all others
# including local_settings (which may end up in the container)
if os.path.exists('/templates/confd_settings.py'):
    sys.path.append('/templates')
    from confd_settings import *  # noqa
