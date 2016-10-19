"""Collection resources."""
from __future__ import absolute_import, division, print_function, unicode_literals

import six

from .base import BaseResource
from .data import Data
from .utils import get_resource_id, resource_list


class BaseCollection(BaseResource):
    """Abstract collection resource.

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

    WRITABLE_FIELDS = ('description', 'settings', 'descriptor_schema',
                       'descriptor') + BaseResource.WRITABLE_FIELDS
    READ_ONLY_FIELDS = ('data', ) + BaseResource.READ_ONLY_FIELDS

    #: ids of data objects (if not hydrated), data objects (if hydrated)
    _data = None
    #: indicates if ``_data`` list is already hydrated
    _data_hydrated = False

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None):
        """Initialize attributes."""
        #: a description
        self.description = None
        #: settings
        self.settings = None
        #: descriptor
        self.descriptor = None
        #: descriptor schema
        self.descriptor_schema = None
        #: collections
        self.collections = None

        BaseResource.__init__(self, slug, id, model_data, resolwe)

    @property
    def data(self):
        """Lazy load ``data`` objects belonging to the collection."""
        if not self._data_hydrated:
            data = self.resolwe.data.filter(id__in=','.join(map(str, self._data or [])))
            # Transform list to ``resource_list``, so the comparison with the
            # original value will work
            self._data = resource_list(data)
            self._data_hydrated = True

        return self._data

    @data.setter
    def data(self, value):
        """Store data ids and set hydration flag to ``False``."""
        self._data = value
        self._data_hydrated = False

    def add_data(self, *data):
        """Add ``data`` objects to the collection."""
        data = [get_resource_id(d) for d in data]
        self.api(self.id).add_data.post({'ids': data})

    def remove_data(self, *data):
        """Remove ``data`` objects from the collection."""
        data = [get_resource_id(d) for d in data]
        self.api(self.id).remove_data.post({'ids': data})

    def data_types(self):
        """Return a list of data types (process_type).

        :rtype: List

        """
        process_types = set(self.resolwe.api.data(id_).get()['process_type'] for id_ in self.data)
        return sorted(process_types)

    def files(self, file_name=None, field_name=None):
        """Return list of files in resource."""
        file_list = []
        for id_ in self.data:
            data = Data(id=id_, resolwe=self.resolwe)
            file_list.extend(fname for fname in data.files(file_name=file_name,
                                                           field_name=field_name))

        return file_list

    def download(self, file_name=None, file_type=None, download_dir=None):
        """Download output files of associated Data objects.

        Download files from the Resolwe server to the download
        directory (defaults to the current working directory).

        :param file_name: name of file
        :type file_name: string
        :param file_type: data object type
        :type file_type: string
        :param download_dir: download path
        :type download_dir: string
        :rtype: None

        Collections can contain multiple Data objects and Data objects
        can contain multiple files. All files are downloaded by default,
        but may be filtered by file name or Data object type:

        * re.collection.get(42).download(file_name='alignment7.bam')
        * re.collection.get(42).download(data_type='bam')

        """
        files = []

        if file_type and not isinstance(file_type, six.string_types):
            raise ValueError("Invalid argument value `file_type`.")

        for id_ in self.data:
            data = Data(id=id_, resolwe=self.resolwe)

            def format_file_type(ofield):
                """Ensure that `ofield` starts with `output`."""
                if ofield is not None and not ofield.startswith('output'):
                    return '.'.join(['output'] + ofield.split('.'))
                else:
                    return ofield

            data_files = data.files(file_name, format_file_type(file_type))
            files.extend(zip(data_files, [id_] * len(data_files)))

        files = ['{}/{}'.format(id_, file_) for file_, id_ in files]
        self.resolwe._download_files(files, download_dir)  # pylint: disable=protected-access

    def print_annotation(self):
        """Provide annotation data."""
        raise NotImplementedError()


class Collection(BaseCollection):
    """Resolwe Collection resource.

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

    endpoint = 'collection'

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None):
        """Initialize attributes."""
        BaseCollection.__init__(self, slug, id, model_data, resolwe)

    def print_annotation(self):
        """Provide annotation data."""
        raise NotImplementedError()
