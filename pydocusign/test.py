"""Utilities to run tests around `pydocusign`."""
import json
import os

import requests

import pydocusign


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


def docusign_client_factory(settings=os.environ):
    """Return :class:`pydocusign.DocuSignClient` using ``settings``.

    The following keys are used in ``settings``:

    * ``PYDOCUSIGN_TEST_ROOT_URL``, defaults to
      'https://demo.docusign.net/restapi/v2'

    * ``PYDOCUSIGN_TEST_USERNAME``

    * ``PYDOCUSIGN_TEST_PASSWORD``

    * ``PYDOCUSIGN_TEST_INTEGRATOR_KEY``

    By default, ``settings`` is ``os.environ``, i.e. environment variables are
    used.

    """
    client = pydocusign.DocuSignClient(
        root_url=settings.get('PYDOCUSIGN_TEST_ROOT_URL',
                              'https://demo.docusign.net/restapi/v2'),
        username=settings['PYDOCUSIGN_TEST_USERNAME'],
        password=settings['PYDOCUSIGN_TEST_PASSWORD'],
        integrator_key=settings['PYDOCUSIGN_TEST_INTEGRATOR_KEY'],
    )
    return client


def generate_notification_callback_body(
        data,
        template='callback.xml',
        diecutter_root='https://diecutter.alwaysdata.net/github',
        template_owner='novapost',
        template_project='pydocusign',
        template_revision='master',
        template_path='pydocusign/templates'):
    """Return custom body content to mimic DocuSign notification callbacks.

    Body content is generated from template, using diecutter web service.

    ``data`` argument is a dictionary of data you expect in the callback.

    ``template`` is template file name, one in ``pydocusign/templates/``
    directory of https://github.com/novapost/pydocusign/tree/master/pydocusign/
    repository.

    Raise exception if a problem occurs during content generation.

    Additional (optional) arguments:

    * ``diecutter_root``: root URL of diecutter, API endpoint.
    * ``template_owner``: Github user that owns the template.
    * ``template_project``: Name of Github project that contains the template.
    * ``template_revision``: Commit id or branch of the template.
    * ``template_path``: directory where the template lives.

    """
    payload = json.dumps(data)
    headers = {'content-type': 'application/json'}
    template_url = '/'.join([
        diecutter_root,
        template_owner,
        template_project,
        template_revision,
        template_path,
        template])
    try:
        response = requests.post(template_url, data=payload, headers=headers)
    except requests.exceptions.RequestException as exception:
        raise Exception(
            'Error while generating notification callback body using '
            'template generation service at URL {url} with data {data}. '
            'Exception is {exception}.'
            .format(url=template_url, data=data, exception=exception)
        )
    if response.status_code != 200:
        raise Exception(
            'Error while generating notification callback body using '
            'template generation service at URL {url} with data {data}. '
            'Response code {status}, body:\n{body}.'
            .format(url=template_url, data=data, status=response.status_code,
                    body=response.text)
        )
    return response.text


def post_notification_callback(callback_url, *args, **kwargs):
    """Post fake notification callback to ``callback_url``, return response.

    Additional required arguments: ``data`` and ``template``.

    For a description of additional (required and optional) arguments, see
    :func:`generate_notification_callback_body`.

    """
    body = generate_notification_callback_body(*args, **kwargs)
    # POST body to callback URL.
    headers = {'content-type': 'text/xml'}
    response = requests.post(callback_url, data=body, headers=headers)
    return response
