"""Utilities to run tests around `pydocusign`."""
import os


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
