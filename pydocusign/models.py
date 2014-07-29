"""Python representations for DocuSign models.

See https://www.docusign.com/developer-center/explore/common-terms

.. note::

   CamelCase is used here to mimic DocuSign names.

"""


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


class SignHereTab(Tab):
    """Tag to have a recipient place his signature in the document."""
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


class Recipient(DocuSignObject):
    """Base class for "recipient" objects.

    DocuSign reference lives at
    https://www.docusign.com/p/RESTAPIGuide/RESTAPIGuide.htm#REST%20API%20References/Recipient%20Parameter.htm

    """


class Signer(Recipient):
    """A recipient who must sign, initial, date or add data to form fields on
    the documents in the envelope.

    DocuSign reference lives at
    https://www.docusign.com/p/RESTAPIGuide/RESTAPIGuide.htm#REST%20API%20References/Recipients/Signers%20Recipient.htm

    """
    attributes = ['clientUserId', 'email', 'name', 'recipientId', 'tabs']

    def __init__(self, clientUserId=None, email='', name='', recipientId=None,
                 tabs=[], userId=None):
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
        self.tabs = tabs

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

        """
        data = {
            'clientUserId': self.clientUserId,
            'email': self.email,
            'name': self.name,
            'recipientId': self.recipientId,
            'tabs': {
                'signHereTabs': [],
            },
        }
        for tab in self.tabs:
            if isinstance(tab, SignHereTab):
                data['tabs']['signHereTabs'].append(tab.to_dict())
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


class Envelope(DocuSignObject):
    """An envelope."""
    attributes = ['documents', 'emailBlurb', 'emailSubject', 'recipients',
                  'status']
    STATUS_SENT = 'sent'
    STATUS_DRAFT = 'draft'

    def __init__(self, documents=[], emailBlurb='', emailSubject='',
                 recipients={}, status=STATUS_SENT, envelopeId=None):
        """Setup."""
        self.documents = documents
        self.emailBlurb = emailBlurb
        self.emailSubject = emailSubject
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
        ...     status=Envelope.STATUS_DRAFT)
        >>> envelope.to_dict() == {
        ...     'documents': [document.to_dict()],
        ...     'emailBlurb': 'This is the email body',
        ...     'emailSubject': 'This is the email subject',
        ...     'recipients': {
        ...         'signers': [signer.to_dict()],
        ...     },
        ...     'status': 'draft',
        ... }
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
                    index = int(recipient_data['routingOrder']) - 1
                    self.recipients[index].userId = recipient_data['userId']

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
