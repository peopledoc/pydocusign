#!/usr/bin/env python
# coding=utf-8
"""Sample script that demonstrates `pydocusign` usage for embedded signing.

See also http://iodocs.docusign.com/APIWalkthrough/embeddedSigning

"""
from __future__ import print_function
import os

import pydocusign
from pydocusign.test import fixtures_dir


# Create a client.
client = pydocusign.DocuSignClient(
    root_url=os.environ.get('PYDOCUSIGN_TEST_ROOT_URL',
                            'https://demo.docusign.net/restapi/v2'),
    username=os.environ['PYDOCUSIGN_TEST_USERNAME'],
    password=os.environ['PYDOCUSIGN_TEST_PASSWORD'],
    integrator_key=os.environ['PYDOCUSIGN_TEST_INTEGRATOR_KEY'],
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
    returnUrl='http://example.com')
print("   Received signing URL: {0}".format(signing_url))
