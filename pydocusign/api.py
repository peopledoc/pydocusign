"""Declaration of API shortcuts.

Everything declared (or imported) in this module is exposed in
:mod:`pydocusign` root package, i.e. available when one does
``import pydocusign``.

Here are the motivations of such an "api" module:

* as a `pydocusign` library user, in order to use `pydocusign`, I just do
  ``import pydocusign``. It is enough for most use cases. I do not need to
  bother with more `pydocusign` internals. I know this API will be maintained,
  documented, and not deprecated/refactored without notice.

* as a `pydocusign` library developer, in order to maintain `pydocusign` API, I
  focus on things declared in :mod:`pydocusign.api`. It is enough. It is
  required. I take care of this API. If there is a change in this API between
  consecutive releases, then I use :class:`DeprecationWarning` and I mention it
  in release notes.

It also means that things not exposed in :mod:`docusign.api` are not part of
the deprecation policy. They can be moved, changed, removed without notice.

"""
from pydocusign.client import DocuSignClient  # NoQA
from pydocusign.models import Document  # NoQA
from pydocusign.models import DocuSignObject  # NoQA
from pydocusign.models import Envelope  # NoQA
from pydocusign.models import EventNotification  # NoQA
from pydocusign.models import Recipient  # NoQA
from pydocusign.models import Signer  # NoQA
from pydocusign.models import Role  # NoQA
from pydocusign.models import SignHereTab  # NoQA
from pydocusign.models import ApproveTab  # NoQA
from pydocusign.models import Tab  # NoQA
from pydocusign.parser import DocuSignCallbackParser  # NoQA
