#!/usr/bin/env python
# coding=utf-8
"""Sample script that demonstrates `pydocusign` usage for embedded signing.

See also http://iodocs.docusign.com/APIWalkthrough/embeddedSigning

"""
from __future__ import print_function
import os
import sha
import uuid

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
callback_url = prompt(
    'DOCUSIGN_TEST_CALLBACK_URL',
    'Envelope callback URL',
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
event_notification = pydocusign.EventNotification(
    url=callback_url,
)
input_document_path = os.path.join(fixtures_dir(), 'test.pdf')
with open(input_document_path, 'rb') as pdf_file:
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
print("   Received UserId for recipient 1: {0}".format(
    envelope.recipients[1].userId))


# Retrieve embedded signing for first recipient.
print("4. Get DocuSign Recipient View")
signing_url = envelope.post_recipient_view(
    routingOrder=1,
    returnUrl=signer_return_url)
print("   Received signing URL for recipient 0: {0}".format(signing_url))
signing_url = envelope.post_recipient_view(
    routingOrder=2,
    returnUrl=signer_return_url)
print("   Received signing URL for recipient 1: {0}".format(signing_url))


# Download signature documents.
print("5. List signature documents.")
document_list = envelope.get_document_list()
print("   Received document list: {0}".format(document_list))
print("6. Download document from DocuSign.")
document = envelope.get_document(document_list[0]['documentId'])
document_sha = sha.new(document.read()).hexdigest()
print("   Document SHA1: {0}".format(document_sha))
document.close()
print("7. Download signature certificate from DocuSign.")
document = envelope.get_certificate()
document_sha = sha.new(document.read()).hexdigest()
print("   Certificate SHA1: {0}".format(document_sha))
document.close()
