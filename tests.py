"""Tests for `pydocusign`."""
import os
import unittest

import pydocusign
from pydocusign.test import docusign_client_factory, fixtures_dir


class TestDocuSignClient(unittest.TestCase):
    """Test suite for :class:`pydocusign.client.DocuSignClient`."""
    def test_api(self):
        """DocuSignClient is part of pydocusign root API."""
        pydocusign.DocuSignClient

    def test_login_information(self):
        """DocuSignClient.login_information() populates account information."""
        docusign = docusign_client_factory()
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
        docusign = docusign_client_factory()
        docusign.login_information()
        with open(os.path.join(fixtures_dir(), 'test.pdf'), 'rb') as pdf_file:
            envelope = pydocusign.Envelope(
                emailSubject='This is the subject',
                emailBlurb='This is the body',
                status=pydocusign.Envelope.STATUS_SENT,
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
