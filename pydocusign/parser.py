"""Utilities to parse DocuSign callback responses."""
from collections import OrderedDict

from bs4 import BeautifulSoup
import dateutil.parser

import pydocusign


class DocuSignCallbackParser(object):
    """Parser for DocuSign callback responses (XML body)."""
    def __init__(self, xml_source):
        #: Raw XML source string.
        self.xml_source = xml_source

        #: BeautifulSoup XML tree.
        self.xml_soup = BeautifulSoup(self.xml_source, ["lxml", "xml"])

    @property
    def envelope_status(self):
        """Envelope status.

        Raise ``ValueError`` if status is not valid.

        """
        status = self.xml_soup.EnvelopeStatus.Status.string
        if status is None:
            raise ValueError('Could not read envelope status from XML.')
        if status not in pydocusign.Envelope.STATUS_LIST:
            raise ValueError('Unknown status {status}'.format(status=status))
        return status

    @property
    def timezone_offset(self):
        """Timezone offset.

        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.timezone_offset
        -7

        """
        return int(self.xml_soup.TimeZoneOffset.string)

    def datetime(self, value):
        """Return datetime converted from string.

        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.datetime('2014-10-06T01:41:40.6076508')
        ... # doctest: +NORMALIZE_WHITESPACE
        datetime.datetime(2014, 10, 6, 1, 41, 40, 607650,
                          tzinfo=tzoffset(None, -25200))
        >>> parser.datetime('2014-10-06T01:41:40.12')
        ... # doctest: +NORMALIZE_WHITESPACE
        datetime.datetime(2014, 10, 6, 1, 41, 40, 120000,
                          tzinfo=tzoffset(None, -25200))

        """
        value = '{datetime}{offset}'.format(
            datetime=value,
            offset=self.timezone_offset)
        return dateutil.parser.parse(value)

    @property
    def time_generated(self):
        """Datetime of callback generation.

        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <EnvelopeStatus>
        ...     <TimeGenerated>2014-10-06T01:41:09.4845071</TimeGenerated>
        ...   </EnvelopeStatus>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.time_generated
        ... # doctest: +NORMALIZE_WHITESPACE
        datetime.datetime(2014, 10, 6, 1, 41, 9, 484507,
                          tzinfo=tzoffset(None, -25200))

        """
        return self.datetime(self.xml_soup.EnvelopeStatus.TimeGenerated.string)

    @property
    def envelope_id(self):
        """Envelope ID

        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <EnvelopeStatus>
        ...     <EnvelopeID>some-uuid</EnvelopeID>
        ...   </EnvelopeStatus>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> print parser.envelope_id
        some-uuid

        """
        return self.xml_soup.EnvelopeStatus.EnvelopeID.string

    def envelope_status_datetime(self, status):
        """Datetime of envelope status, or None.

        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <EnvelopeStatus>
        ...     <RecipientStatuses>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-20T01:10:00.12</Sent>
        ...       </RecipientStatus>
        ...     </RecipientStatuses>
        ...     <Created>2014-10-06T01:10:00.12</Created>
        ...     <Sent>2014-10-06T01:41:09.4845071</Sent>
        ...   </EnvelopeStatus>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.envelope_status_datetime(pydocusign.Envelope.STATUS_CREATED)
        ... # doctest: +NORMALIZE_WHITESPACE
        datetime.datetime(2014, 10, 6, 1, 10, 0, 120000,
                          tzinfo=tzoffset(None, -25200))
        >>> parser.envelope_status_datetime(pydocusign.Envelope.STATUS_SENT)
        ... # doctest: +NORMALIZE_WHITESPACE
        datetime.datetime(2014, 10, 6, 1, 41, 9, 484507,
                          tzinfo=tzoffset(None, -25200))
        >>> parser.envelope_status_datetime('completed') is None
        True

        """
        status_attr = status.title()
        status_soup = self.xml_soup.EnvelopeStatus.find(
            status_attr,
            recursive=False)
        if status_soup:
            return self.datetime(status_soup.string)
        else:
            return None

    def recipient_status_datetime(self, recipient_id, status):
        """Datetime of recipient status, or None.

        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <EnvelopeStatus>
        ...     <RecipientStatuses>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-06T01:10:00.12</Sent>
        ...         <Delivered>2014-10-06T01:41:09.4845071</Delivered>
        ...         <ClientUserId>12</ClientUserId>
        ...    <RecipientId>bc5989a1-d642-4296-b96f-02ae7e3e2e66</RecipientId>
        ...       </RecipientStatus>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-07T01:10:00.12</Sent>
        ...         <Delivered>2014-10-07T01:41:09.4845071</Delivered>
        ...         <Signed>2014-10-07T01:41:09.4845071</Signed>
        ...         <ClientUserId>44</ClientUserId>
        ...    <RecipientId>de5989a1-d642-4296-b96f-02ae7e3e2e72</RecipientId>
        ...       </RecipientStatus>
        ...     </RecipientStatuses>
        ...   </EnvelopeStatus>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.recipient_status_datetime('12', 'sent')
        ... # doctest: +NORMALIZE_WHITESPACE
        datetime.datetime(2014, 10, 6, 1, 10, 0, 120000,
                          tzinfo=tzoffset(None, -25200))
        >>> parser.recipient_status_datetime('12', 'delivered')
        ... # doctest: +NORMALIZE_WHITESPACE
        datetime.datetime(2014, 10, 6, 1, 41, 9, 484507,
                          tzinfo=tzoffset(None, -25200))
        >>> parser.recipient_status_datetime('12', 'signed') is None
        True
        >>> parser.recipient_status_datetime('44', 'delivered')
        ... # doctest: +NORMALIZE_WHITESPACE
        datetime.datetime(2014, 10, 7, 1, 41, 9, 484507,
                          tzinfo=tzoffset(None, -25200))

        """
        status_attr = status.title()
        for recipient_soup in self.xml_soup.EnvelopeStatus \
                                           .RecipientStatuses \
                                           .children:
            try:
                current_recipient_id = recipient_soup.ClientUserId.string
            except AttributeError:
                pass
            else:
                if recipient_id == current_recipient_id:
                    status_soup = recipient_soup.find(
                        status_attr,
                        recursive=False)
                    if status_soup:
                        return self.datetime(status_soup.string)
                    return None
        return None

    def cmp_events(self, left, right):
        """Compare ``left`` and ``right`` events."""
        return cmp(left['datetime'], right['datetime'])

    @property
    def envelope_events(self):
        """Ordered (chronological) list of events for envelope.

        >>> from datetime import datetime
        >>> from dateutil.tz import tzoffset
        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <EnvelopeStatus>
        ...     <RecipientStatuses>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-05T10:00:00.0</Sent>
        ...         <Delivered>2014-10-08T10:00:00.0</Delivered>
        ...         <ClientUserId>12</ClientUserId>
        ...     <RecipientId>bc5989a1-d642-4296-b96f-02ae7e3e2e66</RecipientId>
        ...       </RecipientStatus>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-07T10:00:00.0</Sent>
        ...         <ClientUserId>44</ClientUserId>
        ...     <RecipientId>de5989a1-d642-4296-b96f-02ae7e3e2e72</RecipientId>
        ...       </RecipientStatus>
        ...     </RecipientStatuses>
        ...     <Sent>2014-10-06T10:00:00.0</Sent>
        ...     <Created>2014-10-04T10:00:00.0</Created>
        ...   </EnvelopeStatus>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.envelope_events == [
        ...     {
        ...         'datetime': datetime(2014, 10, 4, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'status': pydocusign.Envelope.STATUS_CREATED,
        ...     },
        ...     {
        ...         'datetime': datetime(2014, 10, 6, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'status': pydocusign.Envelope.STATUS_SENT,
        ...     },
        ... ]
        True

        """
        events = []
        for status in pydocusign.Envelope.STATUS_LIST:
            instant = self.envelope_status_datetime(status)
            if instant:
                events.append({
                    'datetime': instant,
                    'status': status,
                })
        events.sort(self.cmp_events)
        return events

    @property
    def recipient_events(self):
        """Ordered (chronological) list of events for recipients.

        >>> from datetime import datetime
        >>> from dateutil.tz import tzoffset
        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <EnvelopeStatus>
        ...     <RecipientStatuses>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-05T10:00:00.0</Sent>
        ...         <Delivered>2014-10-08T10:00:00.0</Delivered>
        ...         <ClientUserId>12</ClientUserId>
        ...     <RecipientId>bc5989a1-d642-4296-b96f-02ae7e3e2e66</RecipientId>
        ...       </RecipientStatus>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-07T10:00:00.0</Sent>
        ...         <ClientUserId>44</ClientUserId>
        ...     <RecipientId>de5989a1-d642-4296-b96f-02ae7e3e2e72</RecipientId>
        ...       </RecipientStatus>
        ...     </RecipientStatuses>
        ...     <Sent>2014-10-06T10:00:00.0</Sent>
        ...     <Created>2014-10-04T10:00:00.0</Created>
        ...   </EnvelopeStatus>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.recipient_events == [
        ...     {
        ...         'datetime': datetime(2014, 10, 5, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'status': pydocusign.Recipient.STATUS_SENT,
        ...         'recipient': '12',
        ...         'clientUserId': '12',
        ...         'recipientId': 'bc5989a1-d642-4296-b96f-02ae7e3e2e66',
        ...     },
        ...     {
        ...         'datetime': datetime(2014, 10, 7, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'status': pydocusign.Recipient.STATUS_SENT,
        ...         'recipient': '44',
        ...         'clientUserId': '44',
        ...         'recipientId': 'de5989a1-d642-4296-b96f-02ae7e3e2e72',
        ...     },
        ...     {
        ...         'datetime': datetime(2014, 10, 8, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'status': pydocusign.Recipient.STATUS_DELIVERED,
        ...         'recipient': '12',
        ...         'clientUserId': '12',
        ...         'recipientId': 'bc5989a1-d642-4296-b96f-02ae7e3e2e66',
        ...     },
        ... ]
        True

        """
        events = []
        for recipient_soup in self.xml_soup.EnvelopeStatus \
                                           .RecipientStatuses \
                                           .children:
            try:
                recipient_id = recipient_soup.RecipientId.string
                client_user_id = recipient_soup.ClientUserId.string
            except AttributeError:
                pass
            else:
                for status in pydocusign.Recipient.STATUS_LIST:
                    instant = self.recipient_status_datetime(
                        client_user_id, status)
                    if instant:
                        events.append({
                            'datetime': instant,
                            'status': status,
                            'recipient': client_user_id,  # Backward compat.
                            'recipientId': recipient_id,
                            'clientUserId': client_user_id,
                        })
        events.sort(self.cmp_events)
        return events

    @property
    def events(self):
        """Ordered (chronological, from oldest ot latest) list of events.

        >>> from datetime import datetime
        >>> from dateutil.tz import tzoffset
        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <EnvelopeStatus>
        ...     <RecipientStatuses>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-05T10:00:00.0</Sent>
        ...         <Delivered>2014-10-08T10:00:00.0</Delivered>
        ...         <ClientUserId>12</ClientUserId>
        ...     <RecipientId>bc5989a1-d642-4296-b96f-02ae7e3e2e66</RecipientId>
        ...       </RecipientStatus>
        ...       <RecipientStatus>
        ...         <Sent>2014-10-07T10:00:00.0</Sent>
        ...         <ClientUserId>44</ClientUserId>
        ...     <RecipientId>de5989a1-d642-4296-b96f-02ae7e3e2e72</RecipientId>
        ...       </RecipientStatus>
        ...     </RecipientStatuses>
        ...     <Sent>2014-10-06T10:00:00.0</Sent>
        ...     <Created>2014-10-04T10:00:00.0</Created>
        ...   </EnvelopeStatus>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.events == [
        ...     {
        ...         'datetime': datetime(2014, 10, 4, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'object': 'envelope',
        ...         'status': pydocusign.Envelope.STATUS_CREATED,
        ...         'recipient': None,
        ...     },
        ...     {
        ...         'datetime': datetime(2014, 10, 5, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'object': 'recipient',
        ...         'status': pydocusign.Recipient.STATUS_SENT,
        ...         'recipient': '12',
        ...         'recipientId': 'bc5989a1-d642-4296-b96f-02ae7e3e2e66',
        ...         'clientUserId': '12',
        ...     },
        ...     {
        ...         'datetime': datetime(2014, 10, 6, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'object': 'envelope',
        ...         'status': pydocusign.Envelope.STATUS_SENT,
        ...         'recipient': None,
        ...     },
        ...     {
        ...         'datetime': datetime(2014, 10, 7, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'object': 'recipient',
        ...         'status': pydocusign.Recipient.STATUS_SENT,
        ...         'recipient': '44',
        ...         'recipientId': 'de5989a1-d642-4296-b96f-02ae7e3e2e72',
        ...         'clientUserId': '44',
        ...     },
        ...     {
        ...         'datetime': datetime(2014, 10, 8, 10, 0, 0, 0,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...         'object': 'recipient',
        ...         'status': pydocusign.Recipient.STATUS_DELIVERED,
        ...         'recipient': '12',
        ...         'recipientId': 'bc5989a1-d642-4296-b96f-02ae7e3e2e66',
        ...         'clientUserId': '12',
        ...     },
        ... ]
        True

        """
        events = []
        for event in self.envelope_events:
            event['object'] = 'envelope'
            event['recipient'] = None
            events.append(event)
        for event in self.recipient_events:
            event['object'] = 'recipient'
            events.append(event)
        events.sort(self.cmp_events)
        return events

    @property
    def recipients(self):
        """Dictionary of recipients, ordered by routing order.

        >>> from datetime import datetime
        >>> from dateutil.tz import tzoffset
        >>> xml = '''
        ... <DocuSignEnvelopeInformation>
        ...   <EnvelopeStatus>
        ...     <RecipientStatuses>
        ...       <RecipientStatus>
        ...         <RoutingOrder>2</RoutingOrder>
        ...         <Sent>2014-10-06T00:58:28.98</Sent>
        ...         <Status>Sent</Status>
        ...         <RecipientIPAddress />
        ...         <ClientUserId>12</ClientUserId>
        ...       </RecipientStatus>
        ...       <RecipientStatus>
        ...         <RoutingOrder>1</RoutingOrder>
        ...         <Sent>2014-10-07T10:00:00.1</Sent>
        ...         <Status>Sent</Status>
        ...         <RecipientIPAddress />
        ...         <ClientUserId>44</ClientUserId>
        ...       </RecipientStatus>
        ...     </RecipientStatuses>
        ...   </EnvelopeStatus>
        ...   <TimeZone>Pacific Standard Time</TimeZone>
        ...   <TimeZoneOffset>-7</TimeZoneOffset>
        ... </DocuSignEnvelopeInformation>
        ... '''
        >>> parser = DocuSignCallbackParser(xml_source=xml)
        >>> parser.recipients == OrderedDict([
        ...     ('44', {'RoutingOrder': 1,
        ...             'Sent': datetime(2014, 10, 7, 10, 0, 0, 100000,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...             'Status': 'Sent',
        ...             'ClientUserId': '44',
        ...            }),
        ...     ('12', {'RoutingOrder': 2,
        ...             'Sent': datetime(2014, 10, 6, 0, 58, 28, 980000,
        ...                              tzinfo=tzoffset(None, -25200)),
        ...             'Status': 'Sent',
        ...             'ClientUserId': '12',
        ...            }),
        ... ])
        True

        """
        recipients = []
        for recipient_soup in self.xml_soup.EnvelopeStatus \
                                           .RecipientStatuses \
                                           .children:
            try:
                recipient_soup.children
            except AttributeError:  # Not a node.
                continue
            recipient = {}
            # Assign.
            for child_soup in recipient_soup.children:
                if not child_soup.name:
                    continue
                if child_soup.string is None:
                    continue
                recipient[child_soup.name] = child_soup.string
            # Transform.
            recipient['RoutingOrder'] = int(recipient['RoutingOrder'])
            for status in pydocusign.Recipient.STATUS_LIST:
                try:
                    if status == 'Completed':
                        recipient[status] = self.datetime(recipient['Signed'])
                    else:
                        recipient[status] = self.datetime(recipient[status])
                except KeyError:
                    pass
            # Register.
            recipients.append(recipient)
        # Sort by routing order.
        recipients.sort(lambda a, b: cmp(a['RoutingOrder'], b['RoutingOrder']))
        # Return OrderedDict.
        recipients = OrderedDict([(rec['ClientUserId'], rec)
                                  for rec in recipients])
        return recipients
