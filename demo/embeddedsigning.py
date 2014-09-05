#!/usr/bin/env python
# coding=utf-8
"""Sample script that demonstrates `pydocusign` usage for embedded signing.

See also http://iodocs.docusign.com/APIWalkthrough/embeddedSigning

"""
from __future__ import print_function
import os

import pydocusign
from pydocusign.test import fixtures_dir


def prompt(environ_key, description, default):
    try:
        return os.environ[environ_key]
    except KeyError:
        value = raw_input('{description} (default: "{default}"): '.format(
            default=default, description=description))
        if not value:
            return default
        else:
            return value


# Get configuration from environment or prompt the user...
root_url = prompt(
    'PYDOCUSIGN_TEST_ROOT_URL',
    'DocuSign API URL',
    'https://demo.docusign.net/restapi/v2')
username = prompt(
    'PYDOCUSIGN_TEST_USERNAME',
    'DocuSign API username',
    '')
password = prompt(
    'PYDOCUSIGN_TEST_PASSWORD',
    'DocuSign API password',
    '')
integrator_key = prompt(
    'PYDOCUSIGN_TEST_INTEGRATOR_KEY',
    'DocuSign API integrator key',
    '')
callback_url = prompt(
    'PYDOCUSIGN_TEST_CALLBACK_URL',
    'Envelope callback URL',
    '')
signer_return_url = prompt(
    'PYDOCUSIGN_TEST_SIGNER_RETURN_URL',
    'Signer return URL',
    '')


# Create a client.
client = pydocusign.DocuSignClient(
    root_url=root_url,
    username=username,
    password=password,
    integrator_key=integrator_key,
)


# Login. Updates API URLs in client.
print("1. GET /login_information")
login_information = client.login_information()
print("   Received data: {data}".format(data=login_information))


# Prepare list of signers. Ordering matters.
signers = [
    pydocusign.Signer(
        email='john.accentue@example.com',
        name=u'John Accentué',
        recipientId=1,
        clientUserId='something unique',
        tabs=[
            pydocusign.SignHereTab(
                documentId=1,
                pageNumber=1,
                xPosition=100,
                yPosition=100,
            ),
        ],
    ),
]


# Create envelope with embedded signing.
print("2. POST {account}/envelopes")
event_notification = pydocusign.EventNotification(
    url=callback_url,
)
with open(os.path.join(fixtures_dir(), 'test.pdf'), 'rb') as pdf_file:
    envelope = pydocusign.Envelope(
        documents=[
            pydocusign.Document(
                name='document.pdf',
                documentId=1,
                data=pdf_file,
            ),
        ],
        emailSubject='This is the subject',
        emailBlurb='This is the body',
        eventNotification=event_notification,
        status=pydocusign.Envelope.STATUS_SENT,
        recipients=signers,
    )
    client.create_envelope_from_document(envelope)
print("   Received envelopeId {id}".format(id=envelope.envelopeId))


# Update recipient list of envelope: fetch envelope's ``UserId`` from DocuSign.
print("3. GET {account}/envelopes/{envelopeId}/recipients")
envelope.get_recipients()
print("   Received UserId for recipient 0: {0}".format(
    envelope.recipients[0].userId))


# Retrieve embedded signing for first recipient.
print("4. Get DocuSign Recipient View")
signing_url = envelope.post_recipient_view(
    routingOrder=0,
    returnUrl=signer_return_url)
print("   Received signing URL: {0}".format(signing_url))
