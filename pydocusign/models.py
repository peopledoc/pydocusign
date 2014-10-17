"""Python representations for DocuSign models.

See https://www.docusign.com/developer-center/explore/common-terms

.. note::

   CamelCase is used here to mimic DocuSign names.

"""


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
    #: DocuSign client, typically assigned by client itself.
    client = None

    def to_dict(self):
        """Return dict representation of model."""
        data = dict([(k, getattr(self, k)) for k in self.attributes])
        return data

    def __unicode__(self):
        return self.to_dict()


class Tab(DocuSignObject):
    """Base class for DocuSign tabs.

    A tab is a placeholder (signature) or data (form fields) container.

    DocuSign reference lives at
    https://www.docusign.com/p/RESTAPIGuide/RESTAPIGuide.htm#REST%20API%20References/Tab%20Parameters.htm

    """
    tabs_name = None


class PositionnedTab(Tab):
    """Base class for a positionned DocuSign Tab."""
    attributes = ['documentId', 'pageNumber', 'xPosition', 'yPosition']

    def __init__(self, documentId=None, pageNumber=1, xPosition=0,
                 yPosition=0, recipientId=None):
        """Setup."""
        #: Document ID number that the tab is placed on.
        self.documentId = documentId

        #: Page number where the tab will be affixed.
        self.pageNumber = pageNumber

        #: Horizontal offset of the tab on the page, from left.
        self.xPosition = xPosition

        #: Vertical offset of the tab on the page, from top.
        self.yPosition = yPosition


class SignHereTab(PositionnedTab):
    """Tag to have a recipient place his signature in the document."""
    tabs_name = 'signHereTabs'

    def to_dict(self):
        """Return dict representation of model.

        >>> tab = SignHereTab(
        ...     documentId=2,
        ...     pageNumber=1,
        ...     xPosition=100,
        ...     yPosition=200)
        >>> tab.to_dict() == {
        ...     'documentId': 2,
        ...     'pageNumber': 1,
        ...     'xPosition': 100,
        ...     'yPosition': 200,
        ... }
        True

        """
        return super(SignHereTab, self).to_dict()


class ApproveTab(PositionnedTab):
    """Tag to have a recipient approve the document."""
    tabs_name = 'approveTabs'

    def to_dict(self):
        """Return dict representation of model.

        >>> tab = ApproveTab(
        ...     documentId=2,
        ...     pageNumber=1,
        ...     xPosition=100,
        ...     yPosition=200)
        >>> tab.to_dict() == {
        ...     'documentId': 2,
        ...     'pageNumber': 1,
        ...     'xPosition': 100,
        ...     'yPosition': 200,
        ... }
        True

        """
        return super(ApproveTab, self).to_dict()


class Recipient(DocuSignObject):
    """Base class for "recipient" objects.

    DocuSign reference lives at
    https://www.docusign.com/p/RESTAPIGuide/RESTAPIGuide.htm#REST%20API%20References/Recipient%20Parameter.htm

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
    https://www.docusign.com/p/RESTAPIGuide/RESTAPIGuide.htm#REST%20API%20References/Recipients/Signers%20Recipient.htm

    """
    attributes = ['clientUserId', 'email', 'name', 'recipientId', 'tabs']

    def __init__(self, clientUserId=None, email='', name='', recipientId=None,
                 tabs=None, userId=None):
        """Setup."""
        #: If ``None`` then the recipient is remote (email sent) else embedded.
        self.clientUserId = clientUserId

        #: Email of the recipient. Notification will be sent to this email id.
        #: This can be a maximum of 100 characters.
        self.email = email

        #: Full legal name of the recipient. This can be a maximum of 100
        #: characters.
        self.name = name

        #: Unique for the recipient. It is used by the tab element to indicate
        #: which recipient is to sign the Document.
        self.recipientId = recipientId

        #: Specifies the Tabs associated with the recipient. See :class:`Tab`.
        #:
        #: Optional element only used with recipient types
        #: :class:`InPersonSigner` and :class:`Signer`.
        self.tabs = tabs or []

        #: User ID on DocuSign side. It is an UUID.
        self.userId = userId

    def to_dict(self):
        """Return dict representation of model.

        >>> tab = SignHereTab(
        ...     documentId=1,
        ...     pageNumber=2,
        ...     xPosition=100,
        ...     yPosition=200)
        >>> signer = Signer(
        ...     clientUserId='some ID in your DB',
        ...     email='signer@example.com',
        ...     name='My Name',
        ...     recipientId=1,
        ...     tabs=[tab])
        >>> signer.to_dict() == {
        ...     'clientUserId': 'some ID in your DB',
        ...     'email': 'signer@example.com',
        ...     'name': 'My Name',
        ...     'recipientId': 1,
        ...     'tabs': {
        ...         'signHereTabs': [tab.to_dict()],
        ...     }
        ... }
        True
        >>> tab = ApproveTab(
        ...     documentId=1,
        ...     pageNumber=2,
        ...     xPosition=100,
        ...     yPosition=200)
        >>> signer = Signer(
        ...     clientUserId='some ID in your DB',
        ...     email='signer@example.com',
        ...     name='My Name',
        ...     recipientId=1,
        ...     tabs=[tab])
        >>> signer.to_dict() == {
        ...     'clientUserId': 'some ID in your DB',
        ...     'email': 'signer@example.com',
        ...     'name': 'My Name',
        ...     'recipientId': 1,
        ...     'tabs': {
        ...         'approveTabs': [tab.to_dict()],
        ...     }
        ... }
        True

        """
        data = {
            'clientUserId': self.clientUserId,
            'email': self.email,
            'name': self.name,
            'recipientId': self.recipientId,
            'tabs': {
            },
        }
        for tab in self.tabs:
            data['tabs'].setdefault(tab.tabs_name, [])
            data['tabs'][tab.tabs_name].append(tab.to_dict())
        return data


class Document(DocuSignObject):
    """A document to sign."""
    attributes = ['documentId', 'name']

    def __init__(self, documentId=None, name='', data=None):
        """Setup."""
        #: The unique Id for the document in an envelope.
        self.documentId = documentId

        #: The name of the document. This can be a maximum of 100 characters.
        self.name = name

        #: A file wrapper.
        self.data = data

    def to_dict(self):
        """Return dict representation of model.

        >>> document = Document(
        ...     documentId=2,
        ...     name='document.pdf')
        >>> document.to_dict() == {
        ...     'documentId': 2,
        ...     'name': 'document.pdf',
        ... }
        True

        """
        return super(Document, self).to_dict()


class EventNotification(DocuSignObject):
    """Envelope's event notification, typically callback URL and options."""
    attributes = [
        'url',
        'loggingEnabled',
        'requireAcknoledgement',
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

    def __init__(self, url='', loggingEnabled=True, requireAcknoledgement=True,
                 useSoapInterface=False, soapNameSpace='',
                 includeCertificateWithSoap=False,
                 signMessageWithX509Cert=False, includeDocuments=False,
                 includeTimeZone=True,
                 includeSenderAccountAsCustomField=True,
                 envelopeEvents=None,
                 recipientEvents=None):
        """Setup."""
        #: The endpoint where envelope updates are sent.
        self.url = url
        self.loggingEnabled = loggingEnabled
        self.requireAcknoledgement = requireAcknoledgement
        self.useSoapInterface = useSoapInterface
        self.soapNameSpace = soapNameSpace
        self.includeCertificateWithSoap = includeCertificateWithSoap
        self.signMessageWithX509Cert = signMessageWithX509Cert
        self.includeDocuments = includeDocuments
        self.includeTimeZone = includeTimeZone
        self.includeSenderAccountAsCustomField = \
            includeSenderAccountAsCustomField
        if envelopeEvents is None:
            envelopeEvents = DEFAULT_ENVELOPE_EVENTS
        self.envelopeEvents = envelopeEvents
        if recipientEvents is None:
            recipientEvents = DEFAULT_RECIPIENT_EVENTS
        self.recipientEvents = recipientEvents

    def to_dict(self):
        """Return dict representation of model.

        >>> event_notification = EventNotification(
        ...     url='http://example.com',
        ... )
        >>> event_notification.to_dict() == {
        ...     'url': 'http://example.com',
        ...     'loggingEnabled': True,
        ...     'requireAcknoledgement': True,
        ...     'useSoapInterface': False,
        ...     'soapNameSpace': '',
        ...     'includeCertificateWithSoap': False,
        ...     'signMessageWithX509Cert': False,
        ...     'includeDocuments': False,
        ...     'includeTimeZone': True,
        ...     'includeSenderAccountAsCustomField': True,
        ...     'envelopeEvents': [
        ...         {
        ...             'envelopeEventStatusCode': ENVELOPE_STATUS_SENT,
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'envelopeEventStatusCode': 'Delivered',
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'envelopeEventStatusCode': 'Completed',
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'envelopeEventStatusCode': 'Declined',
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'envelopeEventStatusCode': 'Voided',
        ...             'includeDocuments': False,
        ...         },
        ...     ],
        ...     'recipientEvents': [
        ...         {
        ...             'recipientEventStatusCode': 'AuthenticationFailed',
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'recipientEventStatusCode': 'AutoResponded',
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'recipientEventStatusCode': 'Completed',
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'recipientEventStatusCode': 'Declined',
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'recipientEventStatusCode': 'Delivered',
        ...             'includeDocuments': False,
        ...         },
        ...         {
        ...             'recipientEventStatusCode': RECIPIENT_STATUS_SENT,
        ...             'includeDocuments': False,
        ...         },
        ...     ],
        ... }
        True

        """
        return super(EventNotification, self).to_dict()


class Envelope(DocuSignObject):
    """An envelope."""
    attributes = ['documents', 'emailBlurb', 'emailSubject',
                  'eventNotification', 'recipients', 'status']

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

    def __init__(self, documents=[], emailBlurb='', emailSubject='',
                 recipients={}, status=ENVELOPE_STATUS_SENT,
                 envelopeId=None, eventNotification=None):
        """Setup."""
        self.documents = documents
        self.emailBlurb = emailBlurb
        self.emailSubject = emailSubject
        self.eventNotification = eventNotification
        self.recipients = recipients
        self.status = status

        #: ID in DocuSign database.
        self.envelopeId = envelopeId

    def to_dict(self):
        """Return dict representation of model.

        >>> tab = SignHereTab(
        ...     documentId=1,
        ...     pageNumber=1,
        ...     xPosition=100,
        ...     yPosition=100)
        >>> signer = Signer(
        ...     email='signer@example.com',
        ...     name='My Name',
        ...     recipientId=1,
        ...     tabs=[tab])
        >>> document = Document(
        ...     documentId=2,
        ...     name='document.pdf')
        >>> envelope = Envelope(
        ...     documents=[document],
        ...     emailBlurb='This is the email body',
        ...     emailSubject='This is the email subject',
        ...     recipients=[signer],
        ...     status=ENVELOPE_STATUS_DRAFT)
        >>> envelope.to_dict() == {
        ...     'documents': [document.to_dict()],
        ...     'emailBlurb': 'This is the email body',
        ...     'emailSubject': 'This is the email subject',
        ...     'recipients': {
        ...         'signers': [signer.to_dict()],
        ...     },
        ...     'status': ENVELOPE_STATUS_DRAFT,
        ... }
        True
        >>> notification = EventNotification(url='fake')
        >>> envelope.eventNotification = notification
        >>> envelope.to_dict()['eventNotification'] == notification.to_dict()
        True

        """
        data = {
            'status': self.status,
            'emailBlurb': self.emailBlurb,
            'emailSubject': self.emailSubject,
            'documents': [doc.to_dict() for doc in self.documents],
            'recipients': {
                'signers': [],
            },
        }
        if self.eventNotification:
            data['eventNotification'] = self.eventNotification.to_dict()
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
        for recipient_type, recipients in data.items():
            if recipient_type == 'signers':
                for recipient_data in recipients:
                    for rec in self.recipients:
                        if str(rec.clientUserId) == \
                                recipient_data['clientUserId']:
                            rec.userId = recipient_data['userId']

    def post_recipient_view(self, routingOrder, returnUrl, client=None):
        """Use ``client`` to fetch embedded signing URL for recipient.

        If ``client`` is ``None``, :attr:`client` is tried.

        """
        if client is None:
            client = self.client
        recipient = self.recipients[routingOrder - 1]
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
