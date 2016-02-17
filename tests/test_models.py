import unittest

from pydocusign import DocuSignObject, SignHereTab, ApproveTab, Signer, Role, \
    Document, EventNotification, Envelope
from pydocusign.models import ENVELOPE_STATUS_SENT, RECIPIENT_STATUS_SENT, \
    ENVELOPE_STATUS_DRAFT


class SampleObject(DocuSignObject):
    attributes = ['foo', 'bar']
    required_attributes = ['bar']


class DefaultedObject(DocuSignObject):
    attributes = ['foo', 'bar']
    attribute_defaults = {'bar': 'bar'}


class DocuSignObjectTest(unittest.TestCase):
    def test_with_all_members(self):
        obj = SampleObject(foo='foo', bar='bar')
        self.assertEqual(obj.to_dict(), {'foo': 'foo', 'bar': 'bar'})

    def test_with_missing_optional(self):
        obj = SampleObject(bar='bar')
        self.assertEqual(obj.to_dict(), {'bar': 'bar'})

    def test_with_missing_required(self):
        obj = SampleObject(foo='foo')
        self.assertEqual(obj.to_dict(), {'foo': 'foo', 'bar': None})

    def test_default_attribute(self):
        obj = DefaultedObject(foo='foo')
        self.assertEqual(obj.to_dict(), {'foo': 'foo', 'bar': 'bar'})


class TabTest(unittest.TestCase):
    def test_serialize_sign_here_tab(self):
        tab = SignHereTab(
            documentId=2,
            pageNumber=1,
            xPosition=100,
            yPosition=200)
        self.assertEqual(tab.to_dict(), {
            'documentId': 2,
            'recipientId': None,
            'pageNumber': 1,
            'xPosition': 100,
            'yPosition': 200,
        })

    def test_serialize_approve_tab(self):
        tab = ApproveTab(
            documentId=2,
            pageNumber=1,
            xPosition=100,
            yPosition=200)
        self.assertEqual(tab.to_dict(), {
            'documentId': 2,
            'recipientId': None,
            'pageNumber': 1,
            'xPosition': 100,
            'yPosition': 200,
        })


class RecipientsTest(unittest.TestCase):
    def test_serialize_signer(self):
        tab = SignHereTab(
            documentId=1,
            pageNumber=2,
            xPosition=100,
            yPosition=200)
        signer = Signer(
            clientUserId='some ID in your DB',
            email='signer@example.com',
            name='My Name',
            recipientId=1,
            tabs=[tab])
        self.assertEqual(signer.to_dict(), {
            'clientUserId': 'some ID in your DB',
            'email': 'signer@example.com',
            'emailNotification': None,
            'name': 'My Name',
            'recipientId': 1,
            'routingOrder': 0,
            'tabs': {
                'signHereTabs': [tab.to_dict()],
            },
            'accessCode': None,
        })

        tab = ApproveTab(
            documentId=1,
            pageNumber=2,
            xPosition=100,
            yPosition=200)
        signer = Signer(
            clientUserId='some ID in your DB',
            email='signer@example.com',
            emailSubject=u'Subject',
            emailBody=u'Body',
            supportedLanguage='de',
            name='My Name',
            recipientId=1,
            routingOrder=100,
            tabs=[tab],
            accessCode='toto')
        self.assertEqual(signer.to_dict(), {
            'clientUserId': 'some ID in your DB',
            'email': 'signer@example.com',
            'emailNotification': {
                'emailBody': u'Body',
                'emailSubject': u'Subject',
                'supportedLanguage': 'de',
            },
            'name': 'My Name',
            'recipientId': 1,
            'routingOrder': 100,
            'tabs': {
                'approveTabs': [tab.to_dict()],
            },
            'accessCode': 'toto',
        })

    def test_serialize_role(self):
        role = Role(
            clientUserId='some ID in your DB',
            email='signer@example.com',
            name='My Name',
            roleName='Role 1')
        self.assertEqual(role.to_dict(), {
            'clientUserId': 'some ID in your DB',
            'email': 'signer@example.com',
            'emailNotification': None,
            'name': 'My Name',
            'roleName': 'Role 1',
        })

        role = Role(
            clientUserId='some ID in your DB',
            email='signer@example.com',
            emailSubject=u'Subject',
            emailBody=u'Body',
            supportedLanguage='de',
            name='My Name',
            roleName='Role 1')
        self.assertEqual(role.to_dict(), {
            'clientUserId': 'some ID in your DB',
            'email': 'signer@example.com',
            'emailNotification': {
                'emailBody': u'Body',
                'emailSubject': u'Subject',
                'supportedLanguage': 'de',
            },
            'name': 'My Name',
            'roleName': 'Role 1',
        })


class DocumentsTest(unittest.TestCase):
    def test_serialize_document(self):
        document = Document(
            documentId=2,
            name='document.pdf')
        self.assertEqual(document.to_dict(), {
            'documentId': 2,
            'name': 'document.pdf',
        })


class EventNotificationTest(unittest.TestCase):
    maxDiff = None

    def test_serialize_event_notification(self):
        event_notification = EventNotification(
            url='http://example.com',
        )
        self.assertEqual(event_notification.to_dict(), {
            'url': 'http://example.com',
            'loggingEnabled': True,
            'requireAcknowledgement': True,
            'useSoapInterface': False,
            'soapNameSpace': '',
            'includeCertificateWithSoap': False,
            'signMessageWithX509Cert': False,
            'includeDocuments': False,
            'includeTimeZone': True,
            'includeSenderAccountAsCustomField': True,
            'envelopeEvents': [
                {
                    'envelopeEventStatusCode': ENVELOPE_STATUS_SENT,
                    'includeDocuments': False,
                },
                {
                    'envelopeEventStatusCode': 'Delivered',
                    'includeDocuments': False,
                },
                {
                    'envelopeEventStatusCode': 'Completed',
                    'includeDocuments': False,
                },
                {
                    'envelopeEventStatusCode': 'Declined',
                    'includeDocuments': False,
                },
                {
                    'envelopeEventStatusCode': 'Voided',
                    'includeDocuments': False,
                },
            ],
            'recipientEvents': [
                {
                    'recipientEventStatusCode': 'AuthenticationFailed',
                    'includeDocuments': False,
                },
                {
                    'recipientEventStatusCode': 'AutoResponded',
                    'includeDocuments': False,
                },
                {
                    'recipientEventStatusCode': 'Completed',
                    'includeDocuments': False,
                },
                {
                    'recipientEventStatusCode': 'Declined',
                    'includeDocuments': False,
                },
                {
                    'recipientEventStatusCode': 'Delivered',
                    'includeDocuments': False,
                },
                {
                    'recipientEventStatusCode': RECIPIENT_STATUS_SENT,
                    'includeDocuments': False,
                },
            ],
        })


class EnvelopeTest(unittest.TestCase):
    def test_serialize_envelope_with_signer(self):
        tab = SignHereTab(
            documentId=1,
            pageNumber=1,
            xPosition=100,
            yPosition=100)
        signer = Signer(
            email='signer@example.com',
            name='My Name',
            recipientId=1,
            tabs=[tab])
        document = Document(
            documentId=2,
            name='document.pdf')
        envelope = Envelope(
            documents=[document],
            emailBlurb='This is the email body',
            emailSubject='This is the email subject',
            recipients=[signer],
            status=ENVELOPE_STATUS_DRAFT)
        self.assertEqual(envelope.to_dict(), {
            'documents': [document.to_dict()],
            'emailBlurb': 'This is the email body',
            'emailSubject': 'This is the email subject',
            'recipients': {
                'signers': [signer.to_dict()],
            },
            'status': ENVELOPE_STATUS_DRAFT,
        })

        notification = EventNotification(url='fake')
        envelope.eventNotification = notification
        self.assertEqual(
            envelope.to_dict()['eventNotification'], notification.to_dict())

    def test_serialize_envelope_with_role(self):
        role = Role(
            email='signer@example.com',
            name='My Name',
            roleName='Role 1')
        envelope = Envelope(
            emailBlurb='This is the email body',
            emailSubject='This is the email subject',
            templateId='1111-2222-3333-4444',
            templateRoles=[role],
            status=ENVELOPE_STATUS_DRAFT)
        self.assertEqual(envelope.to_dict(), {
            'emailBlurb': 'This is the email body',
            'emailSubject': 'This is the email subject',
            'templateId': '1111-2222-3333-4444',
            'templateRoles': [
                role.to_dict()
            ],
            'status': ENVELOPE_STATUS_DRAFT,
        })

        notification = EventNotification(url='fake')
        envelope.eventNotification = notification
        self.assertEqual(
            envelope.to_dict()['eventNotification'], notification.to_dict())
