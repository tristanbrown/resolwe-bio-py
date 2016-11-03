"""Collection resources."""
from __future__ import absolute_import, division, print_function, unicode_literals

import six

from .base import BaseResource
from .utils import get_data_id, get_sample_id


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
        #: list of data objects - SET THIS IN SUBCLASS
        self.data = []

        super(BaseCollection, self).__init__(slug, id, model_data, resolwe)

    def _clear_data_cache(self):
        """Clear data cache."""
        raise NotImplementedError('This should be implemented in subclass')

    def add_data(self, *data):
        """Add ``data`` objects to the collection."""
        data = [get_data_id(d) for d in data]
        self.api(self.id).add_data.post({'ids': data})
        self._clear_data_cache()

    def remove_data(self, *data):
        """Remove ``data`` objects from the collection."""
        data = [get_data_id(d) for d in data]
        self.api(self.id).remove_data.post({'ids': data})
        self._clear_data_cache()

    def data_types(self):
        """Return a list of data types (process_type).

        :rtype: List

        """
        process_types = set(self.resolwe.api.data(id_).get()['process_type'] for id_ in self.data)
        return sorted(process_types)

    def files(self, file_name=None, field_name=None):
        """Return list of files in resource."""
        file_list = []
        for data in self.data:
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

        for data in self.data:
            data_files = data.files(file_name, file_type)
            files.extend('{}/{}'.format(data.id, file_name) for file_name in data_files)

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

        #: (lazy loaded) list of data object that belong to collection
        self.data = self.resolwe.data.filter(collection=self.id)
        #: (lazy loaded) list of samples that belong to collection
        self.samples = self.resolwe.sample.filter(collections=self.id)

    def update(self):
        """Clear cache and update resource fields from the server."""
        self.data.clear_cache()  # pylint: disable=no-member
        self.samples.clear_cache()

        super(Collection, self).update()

    def _clear_data_cache(self):
        self.data.clear_cache()  # pylint: disable=no-member

    def add_samples(self, *samples):
        """Add `samples` objects to the collection."""
        samples = [get_sample_id(s) for s in samples]
        # XXX: Make in one request when supported on API
        for sample in samples:
            self.resolwe.api.sample(sample).add_to_collection.post({'ids': [self.id]})

        self.samples.clear_cache()

    def remove_samples(self, *samples):
        """Remove ``sample`` objects from the collection."""
        samples = [get_sample_id(s) for s in samples]
        # XXX: Make in one request when supported on API
        for sample in samples:
            self.resolwe.api.sample(sample).remove_from_collection.post({'ids': [self.id]})

        self.samples.clear_cache()

    def print_annotation(self):
        """Provide annotation data."""
        raise NotImplementedError()
