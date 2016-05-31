"""Process"""
from __future__ import absolute_import, division, print_function, unicode_literals

from .utils import _print_input_line
from .base import BaseResource


class Process(BaseResource):

    """Resolwe Process resource.

    One and only one of the identifiers (slug, id or model_data)
    should be given.

    :param slug: Resource slug
    :type slug: str
    :param id: Resource ID
    :type id: int
    :param model_data: Resource model data
    :type model_data: dict
    :param resolwe: Resolwe instance
    :type resolwe: Resolwe object

    """

    endpoint = "process"

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None):
        BaseResource.__init__(self, slug, id, model_data, resolwe)

    def print_inputs(self):
        """Pretty print input_schema."""
        _print_input_line(self.input_schema, 0)  # pylint: disable=no-member
