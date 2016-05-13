"""Sample"""
from __future__ import absolute_import, division, print_function, unicode_literals

from .collection import BaseCollection


class Sample(BaseCollection):
    """
    Resolwe Sample resource.
    """

    endpoint = 'sample'

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None):
        """
        Resolwe Sample resource.

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
        BaseCollection.__init__(self, slug, id, model_data, resolwe)

    def print_annotation(self):
        """
        Provide annotation data.
        """
        raise NotImplementedError()
