"""Utilities to run tests around `pydocusign`."""
import os

import pydocusign


def fixtures_dir():
    """Return absolute path to test fixtures dir, as best guess.

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
