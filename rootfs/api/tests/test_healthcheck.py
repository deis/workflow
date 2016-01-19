
from django.test import TestCase


class HealthCheckTest(TestCase):

    def setUp(self):
        self.url = '/healthz'

    def test_healthcheck(self):
        # GET and HEAD (no auth required)
        resp = self.client.get(self.url)
        self.assertContains(resp, "OK", status_code=200)

        resp = self.client.head(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_healthcheck_invalid(self):
        for method in ('put', 'post', 'patch', 'delete'):
            resp = getattr(self.client, method)(self.url)
            # method not allowed
            self.assertEqual(resp.status_code, 405)
