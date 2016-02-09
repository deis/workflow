import os
import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token

from api.models import App, Certificate, Domain


class CertificateUseCase5Test(TestCase):

    """
    Tests creation of 3 domains (one is a wildcard) and 2 SSL certificate (one is a wildcard).
    Attach each certificate to a matching domain(s) and then deatch.
    """

    fixtures = ['tests.json']

    def setUp(self):
        self.user = User.objects.get(username='autotest')
        self.token = Token.objects.get(user=self.user).key
        self.user2 = User.objects.get(username='autotest2')
        self.token2 = Token.objects.get(user=self.user).key

        self.url = '/v2/certs'
        self.app = App.objects.create(owner=self.user, id='test-app-use-case-5')
        # Done out of scope as it gets the same cert as the wildcard
        Domain.objects.create(owner=self.user, app=self.app, domain='foo.com')
        self.domains = {
            '*.foo.com': Domain.objects.create(owner=self.user, app=self.app, domain='*.foo.com'),
            'bar.com': Domain.objects.create(owner=self.user, app=self.app, domain='bar.com'),
        }

        self.certificates = {}

        path = os.path.dirname(os.path.realpath(__file__))

        # load up the certs
        for domain in self.domains:
            self.certificates[domain] = {'name': domain.replace('.', '-').replace('*', 'wildcard')}
            filename = domain.replace('*', 'wildcard')

            with open('{}/certs/{}.key'.format(path, filename)) as f:
                self.certificates[domain]['key'] = f.read()

            with open('{}/certs/{}.cert'.format(path, filename)) as f:
                self.certificates[domain]['cert'] = f.read()

        # add expires, common_name and fingerprints
        self.certificates['*.foo.com']['expires'] = '2017-01-21T21:56:15UTC'
        self.certificates['*.foo.com']['fingerprint'] = '8F:8E:5F:F6:7A:78:07:5B:75:3E:10:D5:91:AE:30:4A:48:F4:40:39:90:12:88:B3:41:C6:68:7F:62:F5:CD:EB'  # noqa
        self.certificates['*.foo.com']['common_name'] = '*.foo.com'
        self.certificates['*.foo.com']['san'] = ['foo.com']

        self.certificates['bar.com']['expires'] = '2017-01-14T23:57:57UTC'
        self.certificates['bar.com']['fingerprint'] = '7A:CA:B8:50:FF:8D:EB:03:3D:AC:AD:13:4F:EE:03:D5:5D:EB:5E:37:51:8C:E0:98:F8:1B:36:2B:20:83:0D:C0'  # noqa
        self.certificates['bar.com']['common_name'] = 'bar.com'
        self.certificates['bar.com']['san'] = []

    def test_create_certificate_with_domain(self):
        """Tests creating a certificate."""
        for domain, certificate in self.certificates.items():
            response = self.client.post(
                self.url,
                json.dumps({
                    'name': certificate['name'],
                    'certificate': certificate['cert'],
                    'key': certificate['key']
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION='token {}'.format(self.token)
            )
            self.assertEqual(response.status_code, 201)

    def test_get_certificate_screens_data(self):
        """
        When a user retrieves a certificate, only the common name and expiry date should be
        displayed.
        """
        for domain, certificate in self.certificates.items():
            # Create certificate
            response = self.client.post(
                self.url,
                json.dumps({
                    'name': certificate['name'],
                    'certificate': certificate['cert'],
                    'key': certificate['key']
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION='token {}'.format(self.token)
            )
            self.assertEqual(response.status_code, 201)

            # Attach domain to certificate
            response = self.client.post(
                '{}/{}/domain/'.format(self.url, certificate['name']),
                json.dumps({
                    'domain': domain
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION='token {}'.format(self.token)
            )
            self.assertEqual(response.status_code, 201)

            if certificate['san']:
                for san in certificate['san']:
                    response = self.client.post(
                        '{}/{}/domain/'.format(self.url, certificate['name']),
                        json.dumps({
                            'domain': san
                        }),
                        content_type='application/json',
                        HTTP_AUTHORIZATION='token {}'.format(self.token)
                    )
                    self.assertEqual(response.status_code, 201)

            # Assert data
            response = self.client.get(
                '{}/{}'.format(self.url, certificate['name']),
                HTTP_AUTHORIZATION='token {}'.format(self.token)
            )
            self.assertEqual(response.status_code, 200)

            expected = {
                'name': certificate['name'],
                'common_name': certificate['common_name'],
                'expires': certificate['expires'],
                'fingerprint': certificate['fingerprint'],
                'san': certificate['san'],
                'domains': [domain] + certificate['san']
            }
            for key, value in list(expected.items()):
                self.assertEqual(
                    response.data[key],
                    value,
                    '{} - {}'.format(certificate['name'], key)
                )

            # detach domain to certificate
            response = self.client.delete(
                '{}/{}/domain/{}'.format(self.url, certificate['name'], domain),
                content_type='application/json',
                HTTP_AUTHORIZATION='token {}'.format(self.token)
            )
            self.assertEqual(response.status_code, 204)

            if certificate['san']:
                for san in certificate['san']:
                    response = self.client.delete(
                        '{}/{}/domain/{}'.format(self.url, certificate['name'], san),
                        content_type='application/json',
                        HTTP_AUTHORIZATION='token {}'.format(self.token)
                    )
                    self.assertEqual(response.status_code, 204)

            # Assert data
            response = self.client.get(
                '{}/{}'.format(self.url, certificate['name']),
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
        for domain, certificate in self.certificates.items():
            Certificate.objects.create(
                name=certificate['name'],
                owner=self.user,
                common_name=domain,
                certificate=certificate['cert']
            )
            url = '/v2/certs/{}'.format(certificate['name'])
            response = self.client.delete(url, HTTP_AUTHORIZATION='token {}'.format(self.token))
            self.assertEqual(response.status_code, 204)
