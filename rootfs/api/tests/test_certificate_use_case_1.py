import os
import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token

from api.models import App, Certificate, Domain


class CertificateUseCase1Test(TestCase):

    """
    Tests creation of domain SSL certificate and attach the
    certificate to a domain and then deatch
    """

    fixtures = ['tests.json']

    def setUp(self):
        self.user = User.objects.get(username='autotest')
        self.token = Token.objects.get(user=self.user).key
        self.user2 = User.objects.get(username='autotest2')
        self.token2 = Token.objects.get(user=self.user).key

        self.url = '/v2/certs'
        self.app = App.objects.create(owner=self.user, id='test-app-use-case-1')
        self.domain = Domain.objects.create(owner=self.user, app=self.app, domain='foo.com')
        self.name = 'foo-com'  # certificate name

        path = os.path.dirname(os.path.realpath(__file__))
        with open('{}/certs/{}.key'.format(path, self.domain)) as f:
            self.key = f.read()

        with open('{}/certs/{}.cert'.format(path, self.domain)) as f:
            self.cert = f.read()

    def test_create_certificate_with_domain(self):
        """Tests creating a certificate."""
        response = self.client.post(
            self.url,
            json.dumps({
                'name': self.name,
                'certificate': self.cert,
                'key': self.key
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION='token {}'.format(self.token)
        )
        self.assertEqual(response.status_code, 201)

    def test_create_certificate_with_different_common_name(self):
        """
        Make sure common_name is read-only
        """
        response = self.client.post(
            self.url,
            json.dumps({
                'name': self.name,
                'certificate': self.cert,
                'key': self.key,
                'common_name': 'foo.example.com'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION='token {}'.format(self.token)
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['common_name'], 'foo.com')

    def test_get_certificate_screens_data(self):
        """
        When a user retrieves a certificate make sure proper data is returned
        """
        # Create certificate
        response = self.client.post(
            self.url,
            json.dumps({
                'name': self.name,
                'certificate': self.cert,
                'key': self.key
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION='token {}'.format(self.token)
        )
        self.assertEqual(response.status_code, 201)

        # Attach to domain that does not exist
        response = self.client.post(
            '{}/{}/domain/'.format(self.url, self.name),
            json.dumps({
                'domain': 'random.com'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION='token {}'.format(self.token)
        )
        self.assertEqual(response.status_code, 404)

        # Attach domain to certificate
        response = self.client.post(
            '{}/{}/domain/'.format(self.url, self.name),
            json.dumps({
                'domain': str(self.domain)
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION='token {}'.format(self.token)
        )
        self.assertEqual(response.status_code, 201)

        # Assert data
        response = self.client.get(
            '{}/{}'.format(self.url, self.name),
            HTTP_AUTHORIZATION='token {}'.format(self.token)
        )
        self.assertEqual(response.status_code, 200)

        expected = {
            'name': self.name,
            'common_name': str(self.domain),
            'expires': '2017-01-14T23:55:59UTC',
            'fingerprint': 'AC:82:58:80:EA:C4:B9:75:C1:1C:52:48:40:28:15:1D:47:AC:ED:88:4B:D4:72:95:B2:C0:A0:DF:4A:A7:60:B6',  # noqa
            'san': [],
            'domains': ['foo.com']
        }
        for key, value in list(expected.items()):
            self.assertEqual(response.data[key], value, key)

        # detach domain to certificate
        response = self.client.delete(
            '{}/{}/domain/{}'.format(self.url, self.name, self.domain),
            content_type='application/json',
            HTTP_AUTHORIZATION='token {}'.format(self.token)
        )
        self.assertEqual(response.status_code, 204)

        # Assert data
        response = self.client.get(
            '{}/{}'.format(self.url, self.name),
            HTTP_AUTHORIZATION='token {}'.format(self.token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['domains'], [])

    def test_certficate_denied_requests(self):
        """Disallow put/patch requests"""
        response = self.client.put(self.url, HTTP_AUTHORIZATION='token {}'.format(self.token))
        self.assertEqual(response.status_code, 405)
        response = self.client.patch(self.url, HTTP_AUTHORIZATION='token {}'.format(self.token))
        self.assertEqual(response.status_code, 405)

    def test_delete_certificate(self):
        """Destroying a certificate should generate a 204 response"""
        Certificate.objects.create(
            owner=self.user,
            name=self.name,
            certificate=self.cert
        )
        url = '/v2/certs/{}'.format(self.name)
        response = self.client.delete(url, HTTP_AUTHORIZATION='token {}'.format(self.token))
        self.assertEqual(response.status_code, 204)
