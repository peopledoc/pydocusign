#!/usr/bin/env python
# coding=utf-8
"""Sample script that demonstrates `pydocusign` usage for embedded signing.

See also http://iodocs.docusign.com/APIWalkthrough/embeddedSigning

"""
from __future__ import print_function
import hashlib
import os
import uuid

import pydocusign
from pydocusign.test import fixtures_dir

try:
    raw_input
except NameError:
    raw_input = input


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
    'DOCUSIGN_ROOT_URL',
    'DocuSign API URL',
    'https://demo.docusign.net/restapi/v2')
username = prompt(
    'DOCUSIGN_USERNAME',
    'DocuSign API username',
    '')
password = prompt(
    'DOCUSIGN_PASSWORD',
    'DocuSign API password',
    '')
integrator_key = prompt(
    'DOCUSIGN_INTEGRATOR_KEY',
    'DocuSign API integrator key',
    '')
signer_return_url = prompt(
    'DOCUSIGN_TEST_SIGNER_RETURN_URL',
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
        email='jean.francais@example.com',
        name=u'Jean Français',
        recipientId=1,
        clientUserId=str(uuid.uuid4()),  # Something unique in your database.
        tabs=[
            pydocusign.SignHereTab(
                documentId=1,
                pageNumber=1,
                xPosition=100,
                yPosition=100,
            ),
        ],
        emailSubject='Voici un sujet',
        emailBody='Voici un message',
        supportedLanguage='fr',
    ),
    pydocusign.Signer(
        email='paul.english@example.com',
        name=u'Paul English',
        recipientId=2,
        clientUserId=str(uuid.uuid4()),  # Something unique in your database.
        tabs=[],  # No tabs means user places tabs himself in DocuSign UI.
        emailSubject='Here is a subject',
        emailBody='Here is a message',
        supportedLanguage='en',
    ),
]


# Create envelope with embedded signing.
print("2. POST {account}/envelopes")
document_path = os.path.join(fixtures_dir(), 'test.pdf')
document_2_path = os.path.join(fixtures_dir(), 'test2.pdf')
with open(document_path, 'rb') as pdf, open(document_2_path, 'rb') as pdf_2:
    envelope = pydocusign.Envelope(
        documents=[
            pydocusign.Document(
                name='document.pdf',
                documentId=1,
                data=pdf,
            ),
            pydocusign.Document(
                name='document_2.pdf',
                documentId=2,
                data=pdf_2,
            ),
        ],
        emailSubject='This is the subject',
        emailBlurb='This is the body',
        status=pydocusign.Envelope.STATUS_SENT,
        recipients=signers,
    )
    client.create_envelope_from_documents(envelope)
print("   Received envelopeId {id}".format(id=envelope.envelopeId))


# Update recipient list of envelope: fetch envelope's ``UserId`` from DocuSign.
print("3. GET {account}/envelopes/{envelopeId}/recipients")
envelope.get_recipients()
print("   Received UserId for recipient 0: {0}".format(
    envelope.recipients[0].userId))
print("   Received UserId for recipient 1: {0}".format(
    envelope.recipients[1].userId))


# Retrieve embedded signing for first recipient.
print("4. Get DocuSign Recipient View")
signing_url = envelope.post_recipient_view(
    envelope.recipients[0],
    returnUrl=signer_return_url)
print("   Received signing URL for recipient 0: {0}".format(signing_url))
signing_url = envelope.post_recipient_view(
    envelope.recipients[1],
    returnUrl=signer_return_url)
print("   Received signing URL for recipient 1: {0}".format(signing_url))


# Download signature documents.
print("5. List signature documents.")
document_list = envelope.get_document_list()
print("   Received document list: {0}".format(document_list))
print("6. Download documents from DocuSign.")
for signed_document in document_list:
    document = envelope.get_document(signed_document['documentId'])
    document_sha = hashlib.sha1(document.read()).hexdigest()
    print("   Document SHA1: {0}".format(document_sha))
print("7. Download signature certificate from DocuSign.")
document = envelope.get_certificate()
document_sha = hashlib.sha1(document.read()).hexdigest()
print("   Certificate SHA1: {0}".format(document_sha))
