"""Collection"""
from __future__ import absolute_import, division, print_function, unicode_literals

import six

from .base import BaseResource, DOWNLOAD_TYPES
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
        self.data = None

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
        for id_ in self.data:
            data = Data(id=id_, resolwe=self.resolwe)
            file_list.extend(file_name for file_name, _ in data.files())

        return file_list

    def download(self, file_name=None, data_type=None, download_dir=None):
        """
        Download output files of associated Data objects.

        Download files from the Resolwe server to the download
        directory (defaults to the current working directory).

        :param file_name: name of file
        :type file_name: string
        :param file_type: data object type
        :type file_type: tuple or string
        :param download_dir: download path
        :type download_dir: string
        :rtype: None

        Collections can contain multiple Data objects and Data objects
        can contain multiple files. All files are downloaded by default,
        but may be filtered by file name or Data object type:

        * re.collection.get(42).download(file_name='alignment7.bam')
        * re.collection.get(42).download(data_type='bam')

        """
        output_field = None
        files = []

        if data_type:
            if isinstance(data_type, six.string_types) and data_type in DOWNLOAD_TYPES.keys():
                # type is a shortcut (string)
                data_type, output_field = DOWNLOAD_TYPES[data_type]
            elif isinstance(data_type, tuple) and len(data_type) == 2:
                data_type, output_field = data_type
            else:
                raise ValueError("Invalid argument value data_type")

        for id_ in self.data:
            data = Data(id=id_, resolwe=self.resolwe)

            if data_type and data_type != data.process_type:
                continue

            files.extend(data.files(file_name, output_field))

        files = ['{}/{}'.format(self.id, _file) for _file in files]
        self.resolwe.download_files(files, download_dir)

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
