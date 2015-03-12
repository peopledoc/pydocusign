"""Tests for `pydocusign`."""
from datetime import datetime
import json
import os
import unittest
try:
    from unittest import mock
except ImportError:  # Python 2 fallback.
    import mock


from dateutil.tz import tzoffset

import pydocusign
from pydocusign import models
import pydocusign.test


class DocuSignClientTestCase(unittest.TestCase):
    """Test suite for :class:`pydocusign.client.DocuSignClient`."""
    def test_api(self):
        """DocuSignClient is part of pydocusign root API."""
        pydocusign.DocuSignClient

    def test_explicit_options(self):
        """DocuSignClient() uses explicit arguments."""
        explicit_options = {
            'root_url': 'http://example.com',
            'username': 'johndoe',
            'password': 'secret',
            'integrator_key': 'very-secret',
            'account_id': 'some-uuid',
            'app_token': 'some-token',
            'timeout': 300.0,
        }
        client = pydocusign.DocuSignClient(**explicit_options)
        for key, value in explicit_options.items():
            self.assertEqual(getattr(client, key), value)

    def test_environment_options(self):
        """DocuSignClient uses DOCUSIGN_* environment variables."""
        environ_options = {
            'DOCUSIGN_ROOT_URL': 'http://other.example.com',
            'DOCUSIGN_USERNAME': 'pierre paul ou jacques',
            'DOCUSIGN_PASSWORD': 'not-a-secret',
            'DOCUSIGN_INTEGRATOR_KEY': 'not-an-integator-key',
            'DOCUSIGN_ACCOUNT_ID': 'not-an-uuid',
            'DOCUSIGN_APP_TOKEN': 'not-a-token',
            'DOCUSIGN_TIMEOUT': '200.123',
        }
        environ_backup = dict(os.environ).copy()
        try:
            # Alter environment.
            for key, value in environ_options.items():
                os.environ[key] = value
            # Instanciate client.
            client = pydocusign.DocuSignClient()
            # Check environment variables have been used.
            for key, value in environ_options.items():
                attribute = key.lower()[len('DOCUSIGN_'):]
                if attribute == 'timeout':
                    value = float(value)
                self.assertEqual(getattr(client, attribute), value)
        finally:
            # Restore os.environ.
            for key, value in environ_backup.items():
                os.environ[key] = value

    def test_options_priority(self):
        """Explicit arguments to DocuSignClient have priority over env vars."""
        explicit_options = {
            'root_url': 'http://example.com',
            'username': 'johndoe',
            'password': 'secret',
            'integrator_key': 'very-secret',
            'account_id': 'some-uuid',
            'app_token': 'some-token',
            'timeout': 300.0,
        }
        environ_options = {
            'DOCUSIGN_ROOT_URL': 'http://other.example.com',
            'DOCUSIGN_USERNAME': 'pierre paul ou jacques',
            'DOCUSIGN_PASSWORD': 'not-a-secret',
            'DOCUSIGN_INTEGRATOR_KEY': 'not-an-integator-key',
            'DOCUSIGN_ACCOUNT_ID': 'not-an-uuid',
            'DOCUSIGN_APP_TOKEN': 'not-a-token',
            'DOCUSIGN_TIMEOUT': '200.123',
        }
        environ_backup = dict(os.environ).copy()
        try:
            # Alter environment.
            for key, value in environ_options.items():
                os.environ[key] = value
            # Instanciate client with explicit options.
            client = pydocusign.DocuSignClient(**explicit_options)
            # Check.
            for key, value in explicit_options.items():
                self.assertEqual(getattr(client, key), value)
        finally:
            # Restore os.environ.
            for key, value in environ_backup.items():
                os.environ[key] = value

    def test_login_information(self):
        """DocuSignClient.login_information() populates account information."""
        docusign = pydocusign.DocuSignClient()
        result = docusign.login_information()
        self.assertIn('loginAccounts', result)
        self.assertEqual(len(result['loginAccounts']), 1)
        self.assertIn('userName', result['loginAccounts'][0])
        self.assertIn('name', result['loginAccounts'][0])
        self.assertIn('siteDescription', result['loginAccounts'][0])
        self.assertIn('userId', result['loginAccounts'][0])
        self.assertIn('baseUrl', result['loginAccounts'][0])
        self.assertIn('email', result['loginAccounts'][0])
        self.assertIn('isDefault', result['loginAccounts'][0])
        self.assertIn('accountId', result['loginAccounts'][0])
        self.assertEqual(docusign.account_id,
                         result['loginAccounts'][0]['accountId'])
        self.assertNotEqual(docusign.account_url, '')

    def test_create_envelope_from_document_request(self):
        """Request for creating envelope for document has expected format."""
        docusign = pydocusign.DocuSignClient()
        docusign.login_information()
        with open(os.path.join(pydocusign.test.fixtures_dir(), 'test.pdf'),
                  'rb') as pdf_file:
            envelope = pydocusign.Envelope(
                emailSubject='This is the subject',
                emailBlurb='This is the body',
                status=models.ENVELOPE_STATUS_SENT,
                documents=[
                    pydocusign.Document(
                        name='document.pdf',
                        documentId=1,
                        data=pdf_file,
                    ),
                ],
                recipients=[
                    pydocusign.Signer(
                        email='signer@example.com',
                        name='Zorro',
                        recipientId=1,
                        tabs=[
                            pydocusign.SignHereTab(
                                documentId=1,
                                pageNumber=1,
                                xPosition=100,
                                yPosition=100,
                            ),
                            pydocusign.ApproveTab(
                                documentId=1,
                                pageNumber=1,
                                xPosition=100,
                                yPosition=200,
                            ),
                        ],
                    ),
                ])
            parts = docusign._create_envelope_from_document_request(envelope)
        self.assertTrue(parts['url'].startswith(docusign.account_url))
        self.assertTrue(parts['url'].endswith('/envelopes'))
        self.assertEqual(
            parts['headers']['Content-Type'],
            'multipart/form-data; boundary=myboundary')
        self.assertTrue(parts['body'].strip().startswith(
            '--myboundary\r\n'
            'Content-Type: application/json; charset=UTF-8\r\n'
            'Content-Disposition: form-data\r\n'
            '\r\n'
        ))

    def test_timeout(self):
        """DocuSignClient with (too small) timeout raises exception."""
        docusign = pydocusign.DocuSignClient(timeout=0.001)
        self.assertRaises(
            pydocusign.exceptions.DocuSignException,
            docusign.login_information)


class EnvelopetestCase(unittest.TestCase):
    """Test suite for :class:`pydocusign.models.Envelope`."""
    def test_get_recipients(self):
        """Envelope.get_recipients() updates recipients attribute."""
        # Setup fake envelope.
        signers = [
            models.Signer(
                email='paul.english@example.com',
                name=u'Paul English',
                recipientId=32,
                clientUserId='2',
                tabs=[],
                emailSubject='Here is a subject',
                emailBody='Here is a message',
                supportedLanguage='en',
            ),
            models.Signer(
                email='whatever@example.com',
                name=u'This One Will Be Removed',
                recipientId=43,
                clientUserId='3',
                tabs=[],
                supportedLanguage='en',
            ),
        ]
        envelope = models.Envelope(recipients=signers)
        envelope.envelopeId = 'fake-envelope-id'
        # Setup response data, where signers have been updated after envelope
        # object was posted to DocuSign API.
        response_data = {
            "agents": [],
            "carbonCopies": [],
            "certifiedDeliveries": [],
            "currentRoutingOrder": "String content",
            "editors": [],
            "inPersonSigners": [],
            "intermediaries": [],
            "recipientCount": "String content",
            "signers": [
                {
                    "recipientId": "32",
                    "userId": "22",
                    "clientUserId": "2",
                    "roleName": "",
                    "routingOrder": "12",
                    "email": "paul.english@example.com",
                    "name": "Paul English",
                },
                {
                    "recipientId": "31",
                    "userId": "21",
                    "clientUserId": "1",
                    "roleName": "",
                    "routingOrder": "11",
                    "email": "jean@example.com",
                    "name": "Jean",
                },
            ],
        }
        client = pydocusign.DocuSignClient()
        client.get_envelope_recipients = mock.Mock(return_value=response_data)
        result = envelope.get_recipients(client=client)
        assert result is None
        self.assertEqual(len(envelope.recipients), 2)
        self.assertEqual(envelope.recipients[0].clientUserId, '1')
        self.assertEqual(envelope.recipients[0].routingOrder, 11)
        self.assertEqual(envelope.recipients[0].userId, '21')
        self.assertEqual(envelope.recipients[0].recipientId, '31')
        self.assertEqual(envelope.recipients[0].email, 'jean@example.com')
        self.assertEqual(envelope.recipients[0].name, 'Jean')
        self.assertEqual(envelope.recipients[1].clientUserId, '2')
        self.assertEqual(envelope.recipients[1].routingOrder, 12)
        self.assertEqual(envelope.recipients[1].userId, '22')
        self.assertEqual(envelope.recipients[1].recipientId, '32')
        self.assertEqual(envelope.recipients[1].email,
                         'paul.english@example.com')
        self.assertEqual(envelope.recipients[1].name, 'Paul English')


class DocuSignCallbackParserTestCase(unittest.TestCase):
    """Tests around DocuSign callback content parsers.

    At the same time, we use callback templates, so that they are checked too.

    """
    @classmethod
    def setUpClass(cls):
        """Let's generate some callbacks content, once."""
        data_file = os.path.join(pydocusign.test.fixtures_dir(),
                                 'callback-data.json')
        with open(data_file) as data_file_obj:
            data = json.load(data_file_obj)
        cls.xml = pydocusign.test.generate_notification_callback_body(data)

    def test_properties(self):
        """Test parser properties."""
        parser = pydocusign.DocuSignCallbackParser(self.xml)
        self.assertEqual(parser.envelope_status, models.ENVELOPE_STATUS_SENT)
        self.assertEqual(parser.timezone_offset, -7)
        self.assertEqual(
            parser.envelope_id,
            "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
        self.assertEqual(
            parser.envelope_status_datetime(models.ENVELOPE_STATUS_SENT),
            datetime(2014, 10, 6, 1, 10, 0, 12, tzinfo=tzoffset(None, -25200)),
        )
        self.assertEqual(
            parser.recipient_status_datetime(
                'id-jules-cesar',
                models.RECIPIENT_STATUS_SENT),
            datetime(2014, 10, 6, 1, 10, 1, 0, tzinfo=tzoffset(None, -25200)),
        )
