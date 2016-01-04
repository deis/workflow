from __future__ import unicode_literals
import logging

from django.test.runner import DiscoverRunner
import requests


class SilentDjangoTestSuiteRunner(DiscoverRunner):
    """Prevents api log messages from cluttering the console during tests."""

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        """Run tests with all but critical log messages disabled."""
        # hide any log messages less than critical
        logging.disable(logging.ERROR)
        return super(SilentDjangoTestSuiteRunner, self).run_tests(
            test_labels, extra_tests, **kwargs)


def mock_status_ok(*args, **kwargs):
    resp = requests.Response()
    resp.status_code = 200
    resp._content_consumed = True
    return resp


def mock_none(*args, **kwargs):
    return None

from .test_api_middleware import *  # noqa
from .test_app import *  # noqa
from .test_auth import *  # noqa
from .test_build import *  # noqa
from .test_certificate import *  # noqa
from .test_config import *  # noqa
from .test_container import *  # noqa
from .test_domain import *  # noqa
from .test_healthcheck import *  # noqa
from .test_hooks import *  # noqa
from .test_key import *  # noqa
from .test_limits import *  # noqa
from .test_perm import *  # noqa
from .test_release import *  # noqa
from .test_scheduler import *  # noqa
from .test_users import *  # noqa
