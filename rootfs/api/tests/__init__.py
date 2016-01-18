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
