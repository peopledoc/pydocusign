"""Custom exceptions."""


class DocuSignException(Exception):
    """An error occurred with DocuSign API."""


class DocuSignOAuth2Exception(DocuSignException):
    def __init__(self, error_obj):
        self.error_obj = error_obj

    @property
    def error(self):
        return self.error_obj['error']

    @property
    def error_description(self):
        return self.error_obj['error_description']
