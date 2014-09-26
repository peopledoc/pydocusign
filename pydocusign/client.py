"""DocuSign client."""
from collections import namedtuple
from io import BytesIO
import json
import logging

import certifi
import pycurl
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
                 account_url=''):
        """Configure DocuSign client."""
        #: Root URL of DocuSign API.
        self.root_url = root_url
        #: API username.
        self.username = username
        #: API password.
        self.password = password
        #: API integrator key.
        self.integrator_key = integrator_key
        #: API account ID.
        #: This attribute can be guessed via :meth:`login_information`.
        self.account_id = account_id
        #: User's URL, i.e. the one mentioning :attr:`account_id`.
        #: This attribute can be guessed via :meth:`login_information`.
        self.account_url = account_url
        if self.root_url and self.account_id and not self.account_url:
            self.account_url = '{root}/accounts/{account}'.format(
                root=self.root_url,
                account=self.account_id)

    def base_headers(self):
        """Return dictionary of base headers for all HTTP requests."""
        return {
            'Accept': 'application/json',
            'X-DocuSign-Authentication': json.dumps({
                'Username': self.username,
                'Password': self.password,
                'IntegratorKey': self.integrator_key,
            }),
        }

    def login_information(self):
        """Return dictionary of /login_information.

        Populate :attr:`account_id` and :attr:`account_url`.

        """
        url = '{root}/login_information'.format(root=self.root_url)
        headers = self.base_headers()
        headers['Content-Type'] = 'application/json'
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as exception:
            msg = "DocuSign request error: " \
                  "GET {url} failed ; " \
                  "Error: {exception}".format(url=url, exception=exception)
            logger.error(msg)
            raise exceptions.DocuSignException(msg)
        if response.status_code != 200:
            error_data = json.loads(response.text)
            msg = "DocuSign login failed: " \
                  "GET {url} returned {status} ; " \
                  "Error code: {error_code} ; " \
                  "Error message: '{error_msg}'".format(
                      url=url,
                      status=response.status_code,
                      error_code=error_data['errorCode'],
                      error_msg=error_data['message'],
                  )
            logger.error(msg)
            raise exceptions.DocuSignException(msg)
        data = response.json()
        self.account_id = data['loginAccounts'][0]['accountId']
        self.account_url = '{root}/accounts/{account}'.format(
            root=self.root_url,
            account=self.account_id)
        return data

    def _create_envelope_from_document_request(self, envelope):
        """Return parts of the POST request for /envelopes.

        This is encapsultated in a method for test purposes: we do not want to
        post a real request on DocuSign API for each test, whereas we want to
        check that the HTTP request's parts meet the DocuSign specification.

        .. warning::

           Only one document is supported at the moment. This is a limitation
           of `pydocusign`, not of `DocuSign`.

        """
        if not self.account_url:
            self.login_information()
        url = '{account}/envelopes'.format(account=self.account_url)
        data = envelope.to_dict()
        document = envelope.documents[0].data
        document.seek(0)
        file_content = document.read()
        body = str(
            "\r\n"
            "\r\n"
            "--myboundary\r\n"
            "Content-Type: application/json; charset=UTF-8\r\n"
            "Content-Disposition: form-data\r\n"
            "\r\n"
            "{json_data}\r\n"
            "--myboundary\r\n"
            "Content-Type:application/pdf\r\n"
            "Content-Disposition: file; "
            "filename=\"document.pdf\"; "
            "documentid=1 \r\n"
            "\r\n"
            "{file_data}\r\n"
            "--myboundary--\r\n"
            "\r\n".format(json_data=json.dumps(data), file_data=file_content))
        headers = self.base_headers()
        headers['Content-Type'] = "multipart/form-data; boundary=myboundary"
        headers['Content-Length'] = len(body)
        return {
            'url': url,
            'headers': headers,
            'body': body,
        }

    def create_envelope_from_document(self, envelope):
        """POST to /envelopes and return created envelope ID.

        If ``envelope`` has no (or empty) ``envelopeId`` attribute, this
        method sets the value.

        If ``envelope`` has no (or empty) ``client`` attribute, this method
        sets the value.

        """
        parts = self._create_envelope_from_document_request(envelope)
        c = pycurl.Curl()
        c.setopt(pycurl.SSL_VERIFYPEER, 1)
        c.setopt(pycurl.SSL_VERIFYHOST, 2)
        c.setopt(pycurl.CAINFO, certifi.where())
        c.setopt(pycurl.URL, parts['url'])
        c.setopt(
            pycurl.HTTPHEADER,
            ['{key}: {value}'.format(key=key, value=value)
             for (key, value) in parts['headers'].items()])
        c.setopt(pycurl.VERBOSE, 0)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, parts['body'])
        response_body = BytesIO()
        c.setopt(pycurl.WRITEFUNCTION, response_body.write)
        c.perform()
        response_body.seek(0)
        response = Response(
            status_code=c.getinfo(pycurl.HTTP_CODE),
            text=response_body.read())
        c.close()
        if response.status_code != 201:
            raise exceptions.DocuSignException(response)
        response_data = json.loads(response.text)
        if not envelope.client:
            envelope.client = self
        if not envelope.envelopeId:
            envelope.envelopeId = response_data['envelopeId']
        return response_data['envelopeId']

    def get_envelope_recipients(self, envelopeId):
        """GET {account}/envelopes/{envelopeId}/recipients and return JSON."""
        if not self.account_url:
            self.login_information()
        url = '{account}/envelopes/{envelopeId}/recipients' \
              .format(account=self.account_url,
                      envelopeId=envelopeId)
        headers = self.base_headers()
        headers['Content-Type'] = 'application/json'
        response = requests.get(url, headers=headers)
        return response.json()

    def post_recipient_view(self, authenticationMethod=None,
                            clientUserId='', email='', envelopeId='',
                            returnUrl='', userId='', userName=''):
        """POST to {account}/envelopes/{envelopeId}/views/recipient.

        This is the method to start embedded signing for recipient.

        Return JSON from DocuSign response.

        """
        if not self.account_url:
            self.login_information()
        url = '{account}/envelopes/{envelopeId}/views/recipient' \
              .format(account=self.account_url,
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
        headers = self.base_headers()
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()

    def get_envelope_document_list(self, envelopeId):
        """GET the list of envelope's documents."""
        if not self.account_url:
            self.login_information()
        url = '{account}/envelopes/{envelopeId}/documents' \
              .format(account=self.account_url,
                      envelopeId=envelopeId)
        headers = self.base_headers()
        response = requests.get(url, headers=headers)
        return response.json()['envelopeDocuments']

    def get_envelope_document(self, envelopeId, documentId):
        """Download one document in envelope, return file-like object."""
        if not self.account_url:
            self.login_information()
        url = '{account}/envelopes/{envelopeId}/documents/{documentId}' \
              .format(account=self.account_url,
                      envelopeId=envelopeId,
                      documentId=documentId)
        headers = self.base_headers()
        response = requests.get(url, headers=headers, stream=True)
        setattr(response.raw, 'close', response.close)
        return response.raw
