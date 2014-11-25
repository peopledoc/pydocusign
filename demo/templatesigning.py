#!/usr/bin/env python
# coding=utf-8
"""Sample script that demonstrates `pydocusign` usage for template signing.

See also http://iodocs.docusign.com/APIWalkthrough/requestSignatureFromTemplate

"""
from __future__ import print_function
import os
import sha
import uuid

import pydocusign


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
template_id = prompt(
    'PYDOCUSIGN_TEST_TEMPLATE_ID',
    'DocuSign Template ID',
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


# Prepare list of roles. Ordering matters
roles = [
    pydocusign.Role(
        email='jean.francais@example.com',
        name=u'Jean Français',
        roleName='Role 1',
        clientUserId=str(uuid.uuid4()),  # Something unique in your database.
    ),
    pydocusign.Role(
        email='paul.english@example.com',
        name=u'Paul English',
        roleName='Role 2',
        clientUserId=str(uuid.uuid4()),  # Something unique in your database.
    ),
]


# Create envelope with embedded signing.
print("2. POST {account}/envelopes")
event_notification = pydocusign.EventNotification(
    url=callback_url,
)
envelope = pydocusign.Envelope(
    emailSubject='This is the subject',
    emailBlurb='This is the body',
    eventNotification=event_notification,
    status=pydocusign.Envelope.STATUS_SENT,
    templateId=template_id,
    templateRoles=roles,
)
client.create_envelope_from_template(envelope)
print("   Received envelopeId {id}".format(id=envelope.envelopeId))


# Update recipient list of envelope: fetch envelope's ``UserId`` from DocuSign.
print("3. GET {account}/envelopes/{envelopeId}/recipients")
envelope.get_recipients()
print("   Received UserId for recipient 0: {0}".format(
    envelope.templateRoles[0].userId))
print("   Received UserId for recipient 1: {0}".format(
    envelope.templateRoles[1].userId))


# Retrieve template signing for first recipient.
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
