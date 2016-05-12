"""Sample"""
from __future__ import absolute_import, division, print_function, unicode_literals

from .collection import BaseCollection


class Sample(BaseCollection):
    """
    Resolwe Sample resource.
    """

    endpoint = 'sample'

    def __init__(self, resource, resolwe, fields=None):
        """
        Resolwe Sample resource.

        :param response: Sample resource
        :type response: slumber.Resource
        :param resolwe: Resolwe instance
        :type resolwe: Resolwe
        :param fields: Initial field data
        :type fields: dict

        """
        BaseCollection.__init__(self, resource, resolwe, fields)

    def print_annotation(self):
        """
        Provide annotation data.
        """
        raise NotImplementedError()
