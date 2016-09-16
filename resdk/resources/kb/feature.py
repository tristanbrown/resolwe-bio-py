"""KB feature resource."""
from __future__ import absolute_import, division, print_function, unicode_literals

from ..base import BaseResource


class Feature(BaseResource):
    """Knowledge base Feature resource."""

    endpoint = 'kb.feature.admin'
