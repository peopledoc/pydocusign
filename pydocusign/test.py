"""Utilities to run tests around `pydocusign`."""
import json
import os

import requests


def fixtures_dir():
    """Return absolute path to `pydocusign`'s fixtures dir, as best guess.

    This function supports two situations:

    * you use it in code repository's root, i.e. ``fixtures/`` folder is in the
      same folder than ``pydocusign/test.py``.

    * `tox` runs the documentation build, i.e. ``fixtures/`` folder is in the
      code repository's root, whereas ``pydocusign/test.py`` lives somewhere in
      ``.tox/``.

    Other situations are not supported at the moment.

    """
    here = os.path.dirname(os.path.abspath(__file__))
    here_parts = here.split(os.path.sep)
    is_tox = '.tox' in here_parts
    if is_tox:
        tox_index = here_parts.index('.tox')
        project_dir = here
        for i in range(len(here_parts) - tox_index):
            project_dir = os.path.dirname(project_dir)
    else:
        project_dir = os.path.dirname(here)
    return os.path.normpath(os.path.join(project_dir, 'fixtures'))


def generate_notification_callback_body(
        data,
        template_url='http://diecutter.io/github/'
                     'novapost/pydocusign/master/'
                     'pydocusign/templates/callback.xml'):
    """Return custom body content to mimic DocuSign notification callbacks.

    Body content is generated from template, using diecutter web service.

    ``data`` argument is a dictionary of data you expect in the callback.

    ``template_url`` is diecutter's template resource URL, which is typically
    in the form
    ``http://diecutter.io/github/{owner}/{project}/{revision}/{path}``

    Raise exception if a problem occurs during content generation.

    """
    payload = json.dumps(data)
    headers = {'content-type': 'application/json'}
    try:
        response = requests.post(template_url, data=payload, headers=headers)
    except requests.exceptions.RequestException as exception:
        raise Exception(
            'Error while generating notification callback body using '
            'template generation service at URL {url} with data {data}. '
            'Exception is {exception}.'
            .format(url=template_url,
                    data=json.dumps(data),
                    exception=exception)
        )
    if response.status_code != 200:
        raise Exception(
            'Error while generating notification callback body using '
            'template generation service at URL {url} with data {data}. '
            'Response code {status}, body:\n{body}.'
            .format(url=template_url,
                    data=json.dumps(data),
                    status=response.status_code,
                    body=response.text)
        )
    return response.text


def post_notification_callback(callback_url, data, template_url=None):
    """Post fake notification callback to ``callback_url``, return response.

    Additional arguments: ``data`` and ``template_url``. See
    :func:`generate_notification_callback_body`.

    """
    body = generate_notification_callback_body(data, template_url)
    # POST body to callback URL.
    headers = {'content-type': 'text/xml'}
    response = requests.post(callback_url, data=body, headers=headers)
    return response
