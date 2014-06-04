"""Tests for `pydocusign`."""
import os
import unittest

import pydocusign


def fixtures_dir():
    """Return absolute path to test fixtures dir, as best guess.

    This function supports two situations:

    * you use it in code repository's root, i.e. ``demo/`` folder is in the
      same folder than ``pydocusign/tests/__init__.py``.

    * `tox` runs the documentation build, i.e. ``demo/`` folder is in the
      code repository's root, whereas ``pydocusign/tests/__init__.py`` lives in
      ``.tox/...``.

    Other situations are not supported at the moment.

    """
    here = os.path.dirname(os.path.abspath(__file__))
    here_parts = here.split(os.path.sep)
    is_tox = '.tox' in here_parts
    if is_tox:
        tox_index = here_parts.index('.tox')
        project_dir = here
        for i in range(len(here_parts) - tox_index):
            project_dir = os.path.dirname(project_dir)
    else:
        project_dir = os.path.dirname(os.path.dirname(here))
    return os.path.normpath(os.path.join(project_dir, 'fixtures'))


def docusign_client_factory(settings=os.environ):
    """Return :class:`pydocusign.DocuSignClient` using ``settings``.

    The following keys are used:

    * ``PYDOCUSIGN_TEST_ROOT_URL``, defaults to
      'https://demo.docusign.net/restapi/v2'

    * ``PYDOCUSIGN_TEST_USERNAME``

    * ``PYDOCUSIGN_TEST_PASSWORD``

    * ``PYDOCUSIGN_TEST_INTEGRATOR_KEY``

    """
    client = pydocusign.DocuSignClient(
        root_url=settings.get('PYDOCUSIGN_TEST_ROOT_URL',
                              'https://demo.docusign.net/restapi/v2'),
        username=settings['PYDOCUSIGN_TEST_USERNAME'],
        password=settings['PYDOCUSIGN_TEST_PASSWORD'],
        integrator_key=settings['PYDOCUSIGN_TEST_INTEGRATOR_KEY'],
    )
    return client


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
        signers = [{'email': 'signer@example.com', 'name': 'Zorro'}]
        pdf_file = open(os.path.join(fixtures_dir(), 'test.pdf'), 'rb')
        parts = docusign._create_envelope_from_document_request(
            email_subject='This is the subject',
            email_blurb='This is the body',
            document=pdf_file,
            signers=signers)
        self.assertTrue(parts['url'].startswith(docusign.account_url))
        self.assertTrue(parts['url'].endswith('/envelopes'))
        self.assertEqual(
            parts['headers']['Content-Type'],
            'multipart/form-data; boundary=myboundary')
        self.assertTrue(parts['body'].strip().startswith(
            '--myboundary\r\n'
            'Content-Type: application/json\r\n'
            'Content-Disposition: form-data\r\n'
            '\r\n'
        ))
