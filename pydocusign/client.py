"""DocuSign client."""
from collections import namedtuple
import base64
import json
import logging
import os
import warnings

import requests

from pydocusign import exceptions


logger = logging.getLogger(__name__)

Response = namedtuple('Response', ['status_code', 'text'])


class DocuSignClient(object):
    """DocuSign client."""
    def __init__(self,
                 root_url='',
                 username='',
                 password='',
                 integrator_key='',
                 account_id='',
                 account_url='',
                 app_token=None,
                 oauth2_token=None,
                 timeout=None):
        """Configure DocuSign client."""
        #: Root URL of DocuSign API.
        #:
        #: If not explicitely provided or empty, then ``DOCUSIGN_ROOT_URL``
        #: environment variable, if available, is used.
        self.root_url = root_url
        if not self.root_url:
            self.root_url = os.environ.get('DOCUSIGN_ROOT_URL', '')

        #: API username.
        #:
        #: If not explicitely provided or empty, then ``DOCUSIGN_USERNAME``
        #: environment variable, if available, is used.
        self.username = username
        if not self.username:
            self.username = os.environ.get('DOCUSIGN_USERNAME', '')

        #: API password.
        #:
        #: If not explicitely provided or empty, then ``DOCUSIGN_PASSWORD``
        #: environment variable, if available, is used.
        self.password = password
        if not self.password:
            self.password = os.environ.get('DOCUSIGN_PASSWORD', '')

        #: API integrator key.
        #:
        #: If not explicitely provided or empty, then
        #: ``DOCUSIGN_INTEGRATOR_KEY`` environment variable, if available, is
        #: used.
        self.integrator_key = integrator_key
        if not self.integrator_key:
            self.integrator_key = os.environ.get('DOCUSIGN_INTEGRATOR_KEY',
                                                 '')
        #: API account ID.
        #: This attribute can be guessed via :meth:`login_information`.
        #:
        #: If not explicitely provided or empty, then ``DOCUSIGN_ACCOUNT_ID``
        #: environment variable, if available, is used.
        self.account_id = account_id
        if not self.account_id:
            self.account_id = os.environ.get('DOCUSIGN_ACCOUNT_ID', '')

        #: API AppToken.
        #:
        #: If not explicitely provided or empty, then ``DOCUSIGN_APP_TOKEN``
        #: environment variable, if available, is used.
        self.app_token = app_token
        if not self.app_token:
            self.app_token = os.environ.get('DOCUSIGN_APP_TOKEN', '')

        #: OAuth2 Token.
        #:
        #: If not explicitely provided or empty, then ``DOCUSIGN_OAUTH2_TOKEN``
        #: environment variable, if available, is used.
        self.oauth2_token = oauth2_token
        if not self.oauth2_token:
            self.oauth2_token = os.environ.get('DOCUSIGN_OAUTH2_TOKEN', '')

        #: User's URL, i.e. the one mentioning :attr:`account_id`.
        #: This attribute can be guessed via :meth:`login_information`.
        self.account_url = account_url
        if self.root_url and self.account_id and not self.account_url:
            self.account_url = '{root}/accounts/{account}'.format(
                root=self.root_url,
                account=self.account_id)

        # Connection timeout.
        if timeout is None:
            timeout = float(os.environ.get('DOCUSIGN_TIMEOUT', 30))
        self.timeout = timeout

    def get_timeout(self):
        """Return connection timeout."""
        return self._timeout

    def set_timeout(self, value):
        """Set connection timeout. Converts ``value`` to a float.

        Raises :class:`ValueError` in case the value is lower than 0.001.

        """
        if value < 0.001:
            raise ValueError('Cannot set timeout lower than 0.001')
        self._timeout = int(value * 1000) / 1000.

    def del_timeout(self):
        """Remove timeout attribute."""
        del self._timeout

    timeout = property(
        get_timeout,
        set_timeout,
        del_timeout,
        """Connection timeout, in seconds, for HTTP requests to DocuSign's API.

        This is not timeout for full request, only connection.

        Precision is limited to milliseconds:

        >>> client = DocuSignClient(timeout=1.2345)
        >>> client.timeout
        1.234

        Setting timeout lower than 0.001 is forbidden.

        >>> client.timeout = 0.0009  # Doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: Cannot set timeout lower than 0.001

        """
    )

    def base_headers(self, sobo_email=None):
        """Return dictionary of base headers for all HTTP requests.

        :param sobo_email: if specified, will set the appropriate header to act
        on behalf of that user. The authenticated account must have the
        appropriate permissions. See:
        https://docs.docusign.com/esign/guide/authentication/sobo.html
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if self.oauth2_token:
            headers['Authorization'] = 'Bearer ' + self.oauth2_token

            if sobo_email:
                headers['X-DocuSign-Act-As-User'] = sobo_email

        else:
            auth = {
                'Username': self.username,
                'Password': self.password,
                'IntegratorKey': self.integrator_key,
            }

            if sobo_email:
                auth['SendOnBehalfOf'] = sobo_email

            headers['X-DocuSign-Authentication'] = json.dumps(auth)

        return headers

    def _request(self, url, method='GET', headers=None, data=None,
                 json_data=None, expected_status_code=200, sobo_email=None):
        """Shortcut to perform HTTP requests."""
        do_url = '{root}{path}'.format(root=self.root_url, path=url)
        do_request = getattr(requests, method.lower())
        if headers is None:
            headers = {}
        do_headers = self.base_headers(sobo_email)
        do_headers.update(headers)
        if data is not None:
            do_data = json.dumps(data)
        else:
            do_data = None
        try:
            response = do_request(do_url, headers=do_headers, data=do_data,
                                  json=json_data, timeout=self.timeout)
        except requests.exceptions.RequestException as exception:
            msg = "DocuSign request error: " \
                  "{method} {url} failed ; " \
                  "Error: {exception}" \
                  .format(method=method, url=do_url, exception=exception)
            logger.error(msg)
            raise exceptions.DocuSignException(msg)
        if response.status_code != expected_status_code:
            msg = "DocuSign request failed: " \
                  "{method} {url} returned code {status} " \
                  "while expecting code {expected}; " \
                  "Message: {message} ; " \
                  .format(
                      method=method,
                      url=do_url,
                      status=response.status_code,
                      expected=expected_status_code,
                      message=response.text,
                  )
            logger.error(msg)
            raise exceptions.DocuSignException(msg)
        if response.headers.get('Content-Type', '') \
                           .startswith('application/json'):
            return response.json()
        return response.text

    def get(self, *args, **kwargs):
        """Shortcut to perform GET operations on DocuSign API."""
        return self._request(method='GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        """Shortcut to perform POST operations on DocuSign API."""
        return self._request(method='POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        """Shortcut to perform PUT operations on DocuSign API."""
        return self._request(method='PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Shortcut to perform DELETE operations on DocuSign API."""
        return self._request(method='DELETE', *args, **kwargs)

    def login_information(self):
        """Return dictionary of /login_information.

        Populate :attr:`account_id` and :attr:`account_url`.

        """
        url = '/login_information'
        headers = {
        }
        data = self.get(url, headers=headers)
        self.account_id = data['loginAccounts'][0]['accountId']
        self.account_url = '{root}/accounts/{account}'.format(
            root=self.root_url,
            account=self.account_id)
        return data

    @classmethod
    def oauth2_token_request(cls, root_url, username, password,
                             integrator_key):
        url = root_url + '/oauth2/token'
        data = {
            'grant_type': 'password',
            'client_id': integrator_key,
            'username': username,
            'password': password,
            'scope': 'api',
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            raise exceptions.DocuSignOAuth2Exception(response.json())

        return response.json()['access_token']

    @classmethod
    def oauth2_token_revoke(cls, root_url, token):
        url = root_url + '/oauth2/revoke'
        data = {
            'token': token,
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            raise exceptions.DocuSignOAuth2Exception(response.json())

    def get_account_information(self, account_id=None):
        """Return dictionary of /accounts/:accountId.

        Uses :attr:`account_id` (see :meth:`login_information`) if
        ``account_id`` is ``None``.

        """
        if account_id is None:
            account_id = self.account_id
            url = self.account_url
        else:
            url = '/accounts/{accountId}/'.format(accountId=self.account_id)
        return self.get(url)

    def get_account_provisioning(self):
        """Return dictionary of /accounts/provisioning."""
        url = '/accounts/provisioning'
        headers = {
            'X-DocuSign-AppToken': self.app_token,
        }
        return self.get(url, headers=headers)

    def post_account(self, data):
        """Create account."""
        url = '/accounts'
        return self.post(url, data=data, expected_status_code=201)

    def delete_account(self, accountId):
        """Create account."""
        url = '/accounts/{accountId}'.format(accountId=accountId)
        data = self.delete(url)
        return data.strip() == ''

    def _create_envelope_from_documents_request(self, envelope):
        """Return parts of the POST request for /envelopes.

        .. warning::

           Only one document is supported at the moment. This is a limitation
           of `pydocusign`, not of `DocuSign`.

        """
        data = envelope.to_dict()
        documents = []
        for document in envelope.documents:
            documents.append({
                "documentId": document.documentId,
                "name": document.name,
                "fileExtension": "pdf",
                "documentBase64": base64.b64encode(
                    document.data.read()).decode('utf-8')
            })
        data['documents'] = documents
        return data

    def _create_envelope_from_template_request(self, envelope):
        """Return parts of the POST request for /envelopes,
        for creating an envelope from a template.

        """
        return envelope.to_dict()

    def _create_envelope(self, envelope, data):
        """POST to /envelopes and return created envelope ID.

        Called by ``create_envelope_from_document`` and
        ``create_envelope_from_template`` methods.

        """
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes'.format(
            accountId=self.account_id)
        response_data = self._request(
            url, method='POST', json_data=data, expected_status_code=201)

        if not envelope.client:
            envelope.client = self
        if not envelope.envelopeId:
            envelope.envelopeId = response_data['envelopeId']
        return response_data['envelopeId']

    def create_envelope_from_documents(self, envelope):
        """POST to /envelopes and return created envelope ID.

        If ``envelope`` has no (or empty) ``envelopeId`` attribute, this
        method sets the value.

        If ``envelope`` has no (or empty) ``client`` attribute, this method
        sets the value.

        """
        data = self._create_envelope_from_documents_request(envelope)
        return self._create_envelope(envelope, data)

    def create_envelope_from_document(self, envelope):
        warnings.warn("This method will be deprecated, use "
                      "create_envelope_from_documents instead.",
                      DeprecationWarning)
        data = self._create_envelope_from_documents_request(envelope)
        return self._create_envelope(envelope, data)

    def create_envelope_from_template(self, envelope):
        """POST to /envelopes and return created envelope ID.

        If ``envelope`` has no (or empty) ``envelopeId`` attribute, this
        method sets the value.

        If ``envelope`` has no (or empty) ``client`` attribute, this method
        sets the value.

        """
        data = self._create_envelope_from_template_request(envelope)
        return self._create_envelope(envelope, data)

    def void_envelope(self, envelopeId, voidedReason):
        """PUT to /{account}/envelopes/{envelopeId} with 'voided' status and
        voidedReason, and return JSON."""
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}' \
              .format(accountId=self.account_id,
                      envelopeId=envelopeId)
        data = {
            'status': 'voided',
            'voidedReason': voidedReason
        }
        return self.put(url, data=data)

    def get_envelope(self, envelopeId):
        """GET {account}/envelopes/{envelopeId} and return JSON."""
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}' \
              .format(accountId=self.account_id,
                      envelopeId=envelopeId)
        return self.get(url)

    def post_recipient_view(self, authenticationMethod=None,
                            clientUserId='', email='', envelopeId='',
                            returnUrl='', userId='', userName=''):
        """POST to {account}/envelopes/{envelopeId}/views/recipient.

        This is the method to start embedded signing for recipient.

        Return JSON from DocuSign response.

        """
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}/views/recipient' \
              .format(accountId=self.account_id,
                      envelopeId=envelopeId)
        if authenticationMethod is None:
            authenticationMethod = 'none'
        data = {
            'authenticationMethod': authenticationMethod,
            'clientUserId': clientUserId,
            'email': email,
            'envelopeId': envelopeId,
            'returnUrl': returnUrl,
            'userId': userId,
            'userName': userName,
        }
        return self.post(url, data=data, expected_status_code=201)

    def get_envelope_document_list(self, envelopeId):
        """GET the list of envelope's documents."""
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}/documents' \
              .format(accountId=self.account_id,
                      envelopeId=envelopeId)
        data = self.get(url)
        return data['envelopeDocuments']

    def get_envelope_document(self, envelopeId, documentId):
        """Download one document in envelope, return file-like object."""
        if not self.account_url:
            self.login_information()
        url = '{root}/accounts/{accountId}/envelopes/{envelopeId}' \
              '/documents/{documentId}' \
              .format(root=self.root_url,
                      accountId=self.account_id,
                      envelopeId=envelopeId,
                      documentId=documentId)
        headers = self.base_headers()
        response = requests.get(url, headers=headers, stream=True)
        return response.raw

    def get_template(self, templateId):
        """GET the definition of the template."""
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/templates/{templateId}' \
              .format(accountId=self.account_id,
                      templateId=templateId)
        return self.get(url)

    def get_connect_failures(self):
        """GET a list of DocuSign Connect failures."""
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/connect/failures' \
              .format(accountId=self.account_id)
        return self.get(url)['failures']

    def get_envelope_recipients(self, envelopeId):
        """Retrieves the status of all recipients in a single envelope
        and identifies the current recipient in the routing list.

        DocuSign reference:
        https://docs.docusign.com/esign/restapi/Envelopes/EnvelopeRecipients/list/
        """
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}/recipients' \
              .format(accountId=self.account_id,
                      envelopeId=envelopeId)
        return self.get(url)

    def add_envelope_recipients(self, envelopeId, recipients,
                                resend_envelope=False):
        """Add one or more recipients to an envelope

        DocuSign reference:
        https://docs.docusign.com/esign/restapi/Envelopes/EnvelopeRecipients/create/
        """
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}/recipients' \
            .format(accountId=self.account_id,
                    envelopeId=envelopeId)
        if resend_envelope:
            url += '?resend_envelope=true'
        data = {'signers': [recipient.to_dict() for recipient in recipients]}
        return self.post(url, data=data, expected_status_code=201)

    def update_envelope_recipients(self, envelopeId, recipients,
                                   resend_envelope=False):
        """Modify recipients in a draft envelope or correct recipient information
        for an in process envelope

        DocuSign reference:
        https://docs.docusign.com/esign/restapi/Envelopes/EnvelopeRecipients/update/
        """
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}/recipients' \
              .format(accountId=self.account_id,
                      envelopeId=envelopeId)
        if resend_envelope:
            url += '?resend_envelope=true'
        data = {'signers': [recipient.to_dict() for recipient in recipients]}
        return self.put(url, data=data)

    def delete_envelope_recipient(self, envelopeId, recipientId):
        """Deletes one or more recipients from a draft or sent envelope.

        DocuSign reference:
        https://docs.docusign.com/esign/restapi/Envelopes/EnvelopeRecipients/delete/
        """
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}/recipients/' \
              '{recipientId}'.format(accountId=self.account_id,
                                     envelopeId=envelopeId,
                                     recipientId=recipientId)
        return self.delete(url)

    def delete_envelope_recipients(self, envelopeId, recipientIds):
        """Deletes one or more recipients from a draft or sent envelope.

        DocuSign reference:
        https://docs.docusign.com/esign/restapi/Envelopes/EnvelopeRecipients/deleteList/
        """
        if not self.account_url:
            self.login_information()
        url = '/accounts/{accountId}/envelopes/{envelopeId}/recipients' \
            .format(accountId=self.account_id,
                    envelopeId=envelopeId)
        data = {'signers': [{'recipientId': id_} for id_ in recipientIds]}
        return self.delete(url, data=data)
