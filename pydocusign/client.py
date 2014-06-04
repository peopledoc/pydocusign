"""DocuSign client."""
from collections import namedtuple
from io import BytesIO
import json

import pycurl
import requests


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
        response = requests.get(url, headers=headers)
        data = response.json()
        self.account_id = data['loginAccounts'][0]['accountId']
        self.account_url = '{root}/accounts/{account}'.format(
            root=self.root_url,
            account=self.account_id)
        return data

    def _create_envelope_from_document_request(
            self,
            email_subject='',
            email_blurb='',
            document=None,
            signers=[],
            status='sent'):
        """Return parts of the POST request for /envelopes.

        This is encapsultated in a method for test purposes: we do not want to
        post a real request on DocuSign API for each test.

        """
        url = '{account}/envelopes'.format(account=self.account_url)
        data = {
            'status': status,
            'emailBlurb': email_blurb,
            'emailSubject': email_subject,
            'documents': [
                {
                    'name': 'document.pdf',
                    'documentId': '1',
                    'order': '1',
                },
            ],
            'recipients': {
                'signers': [
                    {
                        'email': signers[0]['email'],
                        'name': signers[0]['name'],
                        'recipientId': '1',
                        'tabs': {
                            'signHereTabs': [
                                {
                                    'documentId': '1',
                                    'pageNumber': '1',
                                    'yPosition': '100',
                                    'xPosition': '100',
                                },
                            ],
                        }
                    }
                ],
            },
        }
        document.seek(0)
        file_content = document.read()
        body = str(
            "\r\n"
            "\r\n"
            "--myboundary\r\n"
            "Content-Type: application/json\r\n"
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

    def create_envelope_from_document(
            self,
            email_subject='',
            email_blurb='',
            document=None,
            signers=[],
            status='sent'):
        """Return dictionary response from /envelopes."""
        parts = self._create_envelope_from_document_request(
            email_subject=email_subject,
            email_blurb=email_blurb,
            document=document,
            signers=signers,
            status=status)
        c = pycurl.Curl()
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
        return response
