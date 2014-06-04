# -*- coding: utf-8 -*-
"""Python client for DocuSign signature SAAS platform."""
import pkg_resources


#: Module version, as defined in PEP-0396.
__version__ = pkg_resources.get_distribution(__package__).version


# API shortcuts.
from pydocusign.api import *  # NoQA
