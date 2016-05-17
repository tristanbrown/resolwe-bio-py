"""Collection"""
from __future__ import absolute_import, division, print_function, unicode_literals

from .base import BaseResource
from .data import Data


class BaseCollection(BaseResource):
    """
    Abstract collection resource class BaseCollection.
    """

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None):
        """
        Abstract collection resource class.

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
        BaseResource.__init__(self, slug, id, model_data, resolwe)

    def data_types(self):
        """
        Return a list of data types (process_type).

        :rtype: List
        """
        return sorted(  # pylint: disable=no-member
            set(self.resolwe.api.data(id_).get()['process_type'] for id_ in self.data))  # pylint: disable=no-member

    def files(self):
        """
        Return list of files in resource.
        """
        file_list = []
        for id_ in self.data:  # pylint: disable=no-member
            data = Data(id=id_, resolwe=self.resolwe)
            file_list.extend(data.get_download_list())
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

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None):
        """
        Resolwe Collection resource.

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
