"""Collection"""
from __future__ import absolute_import, division, print_function, unicode_literals

from .base import BaseResource
from .data import Data


class BaseCollection(BaseResource):
    """
    Abstract collection resource class BaseCollection.
    """

    def __init__(self, resource, resolwe, fields=None):
        """
        Abstract collection resource class.

        :param resource: Resource
        :type resource: slumber.Resource
        :param resolwe: Resolwe instance
        :type resolwe: Resolwe object
        :param fields: Initial field data
        :type fields: dict

        """
        BaseResource.__init__(self, resource, resolwe, fields)

    def data_types(self):
        """
        Return a list of data types (process_type).

        :rtype: List
        """
        return sorted(  # pylint: disable=no-member
            set(self.resolwe.api.data(id_).get()['process_type'] for id_ in self.data))  # pylint: disable=no-member

    def files(self, verbose=False):
        """
        Return list of files in resource.
        """
        file_list = []
        for id_ in self.data:  # pylint: disable=no-member
            data = Data(self.resolwe.api.data(id_), self.resolwe)
            file_list += data.get_download_list(verbose=verbose)
        return file_list

    def print_annotation(self):
        """
        Provide annotation data.
        """
        raise NotImplementedError()


class Collection(BaseCollection):
    """
    Resolwe Collection resource.
    """

    endpoint = 'collection'

    def __init__(self, resource, resolwe, fields=None):
        """
        Resolwe Collection resource.

        :param resource: Collection resource
        :type resource: slumber.Resource
        :param resolwe: Resolwe instance
        :type resolwe: Resolwe object
        :param fields: Initial field data
        :type fields: dict

        """
        BaseCollection.__init__(self, resource, resolwe, fields)

    def print_annotation(self):
        """
        Provide annotation data.
        """
        raise NotImplementedError()
