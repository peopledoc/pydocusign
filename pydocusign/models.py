"""Python representations for DocuSign models.

See https://www.docusign.com/developer-center/explore/common-terms

.. note::

   CamelCase is used here to mimic DocuSign names.

"""
from operator import attrgetter


ENVELOPE_STATUS_CREATED = 'Created'
ENVELOPE_STATUS_DRAFT = 'Draft'
ENVELOPE_STATUS_SENT = 'Sent'
ENVELOPE_STATUS_DELIVERED = 'Delivered'
ENVELOPE_STATUS_COMPLETED = 'Completed'
ENVELOPE_STATUS_DECLINED = 'Declined'
ENVELOPE_STATUS_VOIDED = 'Voided'
ENVELOPE_STATUS_LIST = [
    ENVELOPE_STATUS_CREATED,
    ENVELOPE_STATUS_SENT,
    ENVELOPE_STATUS_DELIVERED,
    ENVELOPE_STATUS_COMPLETED,
    ENVELOPE_STATUS_DECLINED,
    ENVELOPE_STATUS_VOIDED,
]


#: Default list of envelope events on which register for notifications.
#:
#: By default: every envelope event.
DEFAULT_ENVELOPE_EVENTS = [
    {'envelopeEventStatusCode': event, 'includeDocuments': False}
    for event in ENVELOPE_STATUS_LIST
    if event not in [ENVELOPE_STATUS_CREATED, ENVELOPE_STATUS_DRAFT]
]


RECIPIENT_STATUS_AUTHENTICATION_FAILED = 'AuthenticationFailed'
RECIPIENT_STATUS_AUTO_RESPONDED = 'AutoResponded'
RECIPIENT_STATUS_SIGNED = 'Signed'
RECIPIENT_STATUS_COMPLETED = 'Completed'
RECIPIENT_STATUS_DECLINED = 'Declined'
RECIPIENT_STATUS_DELIVERED = 'Delivered'
RECIPIENT_STATUS_SENT = 'Sent'
RECIPIENT_STATUS_LIST = [
    RECIPIENT_STATUS_AUTHENTICATION_FAILED,
    RECIPIENT_STATUS_AUTO_RESPONDED,
    RECIPIENT_STATUS_SIGNED,
    RECIPIENT_STATUS_COMPLETED,
    RECIPIENT_STATUS_DECLINED,
    RECIPIENT_STATUS_DELIVERED,
    RECIPIENT_STATUS_SENT,
]


#: Default list of recipient events on which register for notifications.
#:
#: By default: every recipient event.
DEFAULT_RECIPIENT_EVENTS = [
    {'recipientEventStatusCode': event, 'includeDocuments': False}
    for event in RECIPIENT_STATUS_LIST
    if event is not RECIPIENT_STATUS_SIGNED  # Except some events.
]


class DocuSignObject(object):
    """Base class for DocuSign objects."""
    #: API fields. Used to iterate attributes.
    attributes = []

    #: Required attributes. These will be serialized out even if their values
    #: are None
    required_attributes = set()

    #: Default values for attributes which do not get passed to __init__ and
    #: should be something other than None
    attribute_defaults = {}

    #: DocuSign client, typically assigned by client itself.
    client = None

    def __init__(self, **kwargs):
        attribute_defaults = self.get_attribute_defaults()
        for attribute in self.attributes:
            setattr(
                self, attribute,
                kwargs.get(attribute, attribute_defaults.get(attribute, None))
            )

    def to_dict(self):
        """Return dict representation of model.

        Serializes out fields that are not None or marked as required
        """
        return {k: v for k, v in
                self.__dict__.items() if k in self.attributes
                if v is not None or k in self.required_attributes}

    def __unicode__(self):
        return self.to_dict()

    def get_attribute_defaults(self):
        """Get the dict of attribute defaults for this class.

        Defaults to using `self.attribute_defaults`. You may want to override
        this function if you need to provide different defaults for different
        class instances.
        """
        return self.attribute_defaults


class Tab(DocuSignObject):
    """Base class for DocuSign tabs.

    A tab is a placeholder (signature) or data (form fields) container.

    DocuSign reference for all tab types live in the EnvelopeTabs section on:
    https://docs.docusign.com/esign/restapi/Envelopes/EnvelopeTabs/create/

    """
    _common_attributes = [
        'anchorString',
        'anchorXOffset',
        'anchorYOffset',
        'anchorIgnoreIfNotPresent',
        'anchorUnits',
        'conditionalParentLabel',
        'conditionalParentvalue',
        'customTabId',
        'documentId',
        'pageNumber',
        'recipientId',
        'templateLocked',
        'templateRequired',
        'xPosition',
        'yPosition',
        'tabLabel',
    ]

    _formatting_attributes = [
        'bold',
        'font',
        'fontColor',
        'fontSize',
        'italic',
        'underline',
    ]

    required_attributes = {
        'documentId',
        'pageNumber',
        'recipientId',
        'xPosition',
        'yPosition'
    }

    attribute_defaults = {
        'pageNumber': 1,
        'xPosition': 0,
        'yPosition': 0,
    }

    tabs_name = None


class SignHereTab(Tab):
    """Tab to have a recipient place their signature in the document.
    """
    attributes = Tab._common_attributes + [
        'name',
        'optional',
        'scaleValue',
    ]
    tabs_name = 'signHereTabs'


class InitialHereTab(Tab):
    """Tab to have a recipient place their initials in the document.
    """
    attributes = Tab._common_attributes + [
        'name',
        'optional',
        'scaleValue',
    ]
    tabs_name = 'initialHereTabs'


class ApproveTab(Tab):
    """Tab to have a recipient approve the document.
    """
    attributes = Tab._common_attributes + Tab._formatting_attributes + [
        'buttonText',
        'height',
        'width'
    ]
    tabs_name = 'approveTabs'


class FullNameTab(Tab):
    """Tab to show the user's full name.
    """
    attributes = Tab._common_attributes + Tab._formatting_attributes + [
        'name',
    ]
    tabs_name = 'fullNameTabs'


class DateSignedTab(Tab):
    """Tab to show the date the recipient signed the document.
    """
    attributes = Tab._common_attributes + Tab._formatting_attributes + [
        'name',
        'value'
    ]
    tabs_name = 'dateSignedTabs'


class TitleTab(Tab):
    """Tab to show the recipient's title on the document.
    """
    attributes = Tab._common_attributes + Tab._formatting_attributes + [
        'name',
        'value',
        'width'
    ]
    tabs_name = 'titleTabs'


class Recipient(DocuSignObject):
    """Base class for "recipient" objects.

    DocuSign reference lives at
    https://docs.docusign.com/esign/restapi/Envelopes/EnvelopeRecipients/

    """
    # Pseudo-constants.
    STATUS_AUTHENTICATION_FAILED = RECIPIENT_STATUS_AUTHENTICATION_FAILED
    STATUS_AUTO_RESPONDED = RECIPIENT_STATUS_AUTO_RESPONDED
    STATUS_SIGNED = RECIPIENT_STATUS_SIGNED
    STATUS_COMPLETED = RECIPIENT_STATUS_COMPLETED
    STATUS_DECLINED = RECIPIENT_STATUS_DECLINED
    STATUS_DELIVERED = RECIPIENT_STATUS_DELIVERED
    STATUS_SENT = RECIPIENT_STATUS_SENT
    STATUS_LIST = RECIPIENT_STATUS_LIST
    DEFAULT_EVENTS = DEFAULT_RECIPIENT_EVENTS


class Signer(Recipient):
    """A recipient who must sign, initial, date or add data to form fields on
    the documents in the envelope.

    DocuSign reference lives at
    https://docs.docusign.com/esign/restapi/Envelopes/EnvelopeRecipients/#signers-recipient

    """
    attributes = ['clientUserId', 'email', 'emailBody', 'emailSubject', 'name',
                  'recipientId', 'routingOrder', 'supportedLanguage', 'tabs',
                  'accessCode', 'userId']

    attribute_defaults = {
        'name': '',
        'routingOrder': 0
    }

    def __init__(self, **kwargs):
        super(Signer, self).__init__(**kwargs)
        if self.tabs is None:
            self.tabs = []

    def to_dict(self):
        """Return dict representation of model. """
        data = {
            'clientUserId': self.clientUserId,
            'email': self.email,
            'emailNotification': None,
            'name': self.name,
            'recipientId': self.recipientId,
            'routingOrder': self.routingOrder,
            'tabs': {},
            'accessCode': self.accessCode,
        }
        if self.emailBody or self.emailSubject or self.supportedLanguage:
            data['emailNotification'] = {
                'emailBody': self.emailBody,
                'emailSubject': self.emailSubject,
                'supportedLanguage': self.supportedLanguage,
            }
        for tab in self.tabs:
            data['tabs'].setdefault(tab.tabs_name, [])
            data['tabs'][tab.tabs_name].append(tab.to_dict())
        return data


class Role(Recipient):
    """A recipient who must sign, initial, date or add data to form fields on
    the documents in the envelope template.

    DocuSign reference lives at
    https://docs.docusign.com/esign/restapi/Envelopes/Envelopes/create/
    (Definitions / templateRoles)

    """
    attributes = ['clientUserId', 'email', 'emailBody', 'emailSubject', 'name',
                  'supportedLanguage', 'roleName']

    def to_dict(self):
        """Return dict representation of model."""
        data = {
            'clientUserId': self.clientUserId,
            'email': self.email,
            'emailNotification': None,
            'name': self.name,
            'roleName': self.roleName,
        }
        if self.emailBody or self.emailSubject or self.supportedLanguage:
            data['emailNotification'] = {
                'emailBody': self.emailBody,
                'emailSubject': self.emailSubject,
                'supportedLanguage': self.supportedLanguage,
            }
        return data


class Document(DocuSignObject):
    """A document to sign."""
    attributes = ['documentId', 'name']

    def __init__(self, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.data = kwargs.get('data', None)


class EventNotification(DocuSignObject):
    """Envelope's event notification, typically callback URL and options."""
    attributes = [
        'url',
        'loggingEnabled',
        'requireAcknowledgement',
        'useSoapInterface',
        'soapNameSpace',
        'includeCertificateWithSoap',
        'signMessageWithX509Cert',
        'includeDocuments',
        'includeTimeZone',
        'includeSenderAccountAsCustomField',
        'envelopeEvents',
        'recipientEvents',
    ]
    attribute_defaults = {
        'url': '',
        'loggingEnabled': True,
        'requireAcknowledgement': True,
        'useSoapInterface': False,
        'soapNameSpace': '',
        'includeCertificateWithSoap': False,
        'signMessageWithX509Cert': False,
        'includeDocuments': False,
        'includeTimeZone': True,
        'includeSenderAccountAsCustomField': True,
        'envelopeEvents': DEFAULT_ENVELOPE_EVENTS,
        'recipientEvents': DEFAULT_RECIPIENT_EVENTS,
    }


class Envelope(DocuSignObject):
    """An envelope."""
    attributes = ['documents', 'emailBlurb', 'emailSubject',
                  'eventNotification', 'recipients', 'templateId',
                  'templateRoles', 'status', 'envelopeId', 'userId',
                  'enableWetSign']
    required_attributes = ['envelopeId', 'userId']
    attribute_defaults = {
        'emailBlurb': '',
        'emailSubject': '',
        'status': ENVELOPE_STATUS_SENT,
        'enableWetSign': False,
    }

    # Pseudo-constants.
    STATUS_CREATED = ENVELOPE_STATUS_CREATED
    STATUS_DRAFT = ENVELOPE_STATUS_DRAFT
    STATUS_SENT = ENVELOPE_STATUS_SENT
    STATUS_DELIVERED = ENVELOPE_STATUS_DELIVERED
    STATUS_COMPLETED = ENVELOPE_STATUS_COMPLETED
    STATUS_DECLINED = ENVELOPE_STATUS_DECLINED
    STATUS_VOIDED = ENVELOPE_STATUS_VOIDED
    STATUS_LIST = ENVELOPE_STATUS_LIST
    DEFAULT_EVENTS = DEFAULT_ENVELOPE_EVENTS

    def __init__(self, sobo_email=None, **kwargs):
        """Setup."""
        super(Envelope, self).__init__(**kwargs)
        if self.documents is None:
            self.documents = []
        if self.recipients is None:
            self.recipients = {}

        #: Email address of user to send on behalf of.
        #: If None, will use logged in user.
        self.sobo_email = sobo_email

    def to_dict(self):
        """Return dict representation of model."""
        data = {
            'status': self.status,
            'emailBlurb': self.emailBlurb,
            'emailSubject': self.emailSubject,
        }
        if self.eventNotification:
            data['eventNotification'] = self.eventNotification.to_dict()
        if self.templateId:
            data.update({
                'templateId': self.templateId,
                'templateRoles': [],
            })
            for role in self.templateRoles:
                if isinstance(role, Role):
                    data['templateRoles'].append(role.to_dict())
        else:
            data.update({
                'documents': [doc.to_dict() for doc in self.documents],
                'recipients': {
                    'signers': [],
                },
            })
            for recipient in self.recipients:
                if isinstance(recipient, Signer):
                    data['recipients']['signers'].append(recipient.to_dict())
        return data

    def get_recipients(self, client=None):
        """Use client to fetch and update info about recipients.

        If ``client`` is ``None``, :attr:`client` is tried.

        .. warning::

           This is currently a partial update. It supports only some recipient
           types (signers) and some fields (userId). At the moment, it updates
           the list of recipients, it does not replace the current list with
           data from DocuSign, i.e. if another thread updates the envelope,
           this method will fail.

           This partial implementation is enough to cover current `pydocusign`
           features. Feel free to pull request if you need something better ;)

        """
        if client is None:
            client = self.client
        data = client.get_envelope_recipients(self.envelopeId)
        if self.templateId:
            initial_recipients = self.templateRoles
        else:
            initial_recipients = self.recipients
        synced_recipients = []
        for recipient_data in data.get('signers', []):
            recipient = Signer()
            client_user_id = recipient_data.get('clientUserId', None)
            if client_user_id:
                for index, initial_recipient in enumerate(initial_recipients):
                    if initial_recipient.clientUserId == client_user_id:
                        recipient = initial_recipient
                        del(initial_recipients[index])
                        break
            recipient.routingOrder = int(recipient_data.get('routingOrder', 1))
            recipient.name = recipient_data.get('name', '')
            recipient.userId = recipient_data.get('userId', None)
            recipient.recipientId = recipient_data.get('recipientId', None)
            recipient.clientUserId = recipient_data.get('clientUserId', None)
            recipient.email = recipient_data.get('email', None)
            recipient.roleName = recipient_data.get('roleName', None)
            synced_recipients.append(recipient)

        synced_recipients.sort(key=attrgetter('routingOrder'))
        self.recipients = synced_recipients

    def post_recipient_view(self, recipient, returnUrl, client=None):
        """Use ``client`` to fetch embedded signing URL for recipient.

        If ``client`` is ``None``, :attr:`client` is tried.

        """
        if client is None:
            client = self.client
        response_data = client.post_recipient_view(
            envelopeId=self.envelopeId,
            clientUserId=recipient.clientUserId,
            email=recipient.email,
            userId=recipient.userId,
            userName=recipient.name,
            returnUrl=returnUrl,
        )
        return response_data['url']

    def get_document_list(self, client=None):
        """Use ``client`` to fetch document list."""
        if client is None:
            client = self.client
        return client.get_envelope_document_list(self.envelopeId)

    def get_document(self, documentId, client=None):
        """Use ``client`` to download one document."""
        if client is None:
            client = self.client
        return client.get_envelope_document(self.envelopeId, documentId)

    def get_certificate(self, client=None):
        """Use ``client`` to download special document: certificate."""
        return self.get_document(documentId='certificate', client=client)

    def void(self, voidReason, client=None):
        """Use ``client`` to fetch embedded signing URL for recipient.

        If ``client`` is ``None``, :attr:`client` is tried.

        """
        if client is None:
            client = self.client
        return client.void_envelope(self.envelopeId, voidReason)
