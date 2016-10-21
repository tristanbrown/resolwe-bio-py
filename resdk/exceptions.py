""".. Ignore pydocstyle D400.

==========
Exceptions
==========

Custom ReSDK exceptions.

.. autoclass:: ValidationError

"""
from __future__ import absolute_import, division, print_function


class ValidationError(Exception):
    """An error while validating data."""
