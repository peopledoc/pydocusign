import unittest
try:
    from unittest import mock
except ImportError:  # Python 2 fallback.
    import mock

from pydocusign import DocuSignClient, Signer


class DocuSignTestClient(DocuSignClient):
    def login_information(self):
        self.account_id = 'test'
        self.account_url = '{root}/accounts/test'.format(root=self.root_url)


class ClientRequestTest(unittest.TestCase):
    def test_create_envelope_recipients(self):
        client = DocuSignTestClient()

        with mock.patch.object(client, 'post') as post_mock:
            signers = [
                Signer(clientUserId='userid_2', email='signer1@example.com',
                       name='Signer 2'),
                Signer(clientUserId='userid_2', email='signer2@example.com',
                       name='Signer 2'),
            ]
            client.add_envelope_recipients('ABC123', signers)

        url = '/accounts/{account_id}/envelopes/ABC123/recipients'.format(
            account_id=client.account_id)

        post_mock.assert_called_once_with(
            url,
            data={'signers': [signers[0].to_dict(), signers[1].to_dict()]},
            expected_status_code=201
        )

        with mock.patch.object(client, 'post') as post_mock:
            client.add_envelope_recipients('ABC123', [], resend_envelope=True)

        post_mock.assert_called_once_with(
            '/accounts/{}/envelopes/ABC123/recipients'
            '?resend_envelope=true'.format(client.account_id),
            data={'signers': []},
            expected_status_code=201
        )

    def test_update_envelope_recipients(self):
        client = DocuSignTestClient()

        with mock.patch.object(client, 'put') as put_mock:
            signers = [
                Signer(clientUserId='userid_2', email='signer1@example.com',
                       name='Signer 2'),
                Signer(clientUserId='userid_2', email='signer2@example.com',
                       name='Signer 2'),
            ]
            client.update_envelope_recipients('ABC123', signers)

        url = '/accounts/{account_id}/envelopes/ABC123/recipients'.format(
            account_id=client.account_id)

        put_mock.assert_called_once_with(
            url, data={'signers': [signers[0].to_dict(), signers[1].to_dict()]}
        )

        with mock.patch.object(client, 'put') as put_mock:
            client.update_envelope_recipients('ABC123', [], resend_envelope=True)

        put_mock.assert_called_once_with(
            '/accounts/{}/envelopes/ABC123/recipients'
            '?resend_envelope=true'.format(client.account_id),
            data={'signers': []}
        )

    def test_delete_envelope_recipient(self):
        client = DocuSignTestClient()

        with mock.patch.object(client, 'delete') as delete_mock:
            client.delete_envelope_recipient('ABC123', '1')

        url = '/accounts/{account_id}/envelopes/ABC123/recipients/1'.format(
            account_id=client.account_id)

        delete_mock.assert_called_once_with(url)

    def test_delete_envelope_recipients(self):
        client = DocuSignTestClient()

        with mock.patch.object(client, 'delete') as delete_mock:
            client.delete_envelope_recipients('ABC123', ['1', '2'])

        url = '/accounts/{account_id}/envelopes/ABC123/recipients'.format(
            account_id=client.account_id)

        delete_mock.assert_called_once_with(
            url, data={'signers': [{'recipientId': '1'}, {'recipientId': '2'}]}
        )

    def test_get_page_image(self):
        client = DocuSignTestClient()

        with mock.patch.object(client, 'get') as get_mock:
            client.get_page_image('ABC123', 1, 1, 72, max_height=300)

        url = '/accounts/{accountId}/envelopes/ABC123/documents/1/pages/1/' \
              'page_image?dpi=72&max_height=300'\
            .format(accountId=client.account_id)

        get_mock.assert_called_once_with(url)
