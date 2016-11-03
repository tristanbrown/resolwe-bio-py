"""Sample resource."""
from __future__ import absolute_import, division, print_function, unicode_literals

from .collection import BaseCollection


class Sample(BaseCollection):
    """Resolwe Sample resource.

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

    endpoint = 'sample'

    WRITABLE_FIELDS = ('presample', ) + BaseCollection.WRITABLE_FIELDS

    #: ids of collections objects (if not hydrated), collections objects (if hydrated)
    _collections = None
    #: (lazy loaded) list of data object that belong to sample
    _data = None

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None, presample=False):
        """Initialize attributes."""
        self.endpoint = 'presample' if presample else 'sample'

        self.presample = presample

        super(Sample, self).__init__(slug, id, model_data, resolwe)

    def update(self):
        """Clear cache and update resource fields from the server."""
        self._collections = None
        self._data = None

        super(Sample, self).update()

    @property
    def collections(self):
        """Lazy load `collection` objects to which sample belongs."""
        if not self._collections:
            self._collections = self.resolwe.collection.filter(sample=self.id)

        return self._collections

    @property
    def data(self):
        """Lazy load ``data`` objects belonging to the collection."""
        if not self._data:
            self._data = self.resolwe.data.filter(sample=self.id)

        return self._data

    def print_annotation(self):
        """Provide annotation data."""
        raise NotImplementedError()

    def update_descriptor(self, descriptor):
        """Update descriptor and descriptor_schema."""
        self.api(self.id).patch({'descriptor': descriptor})

    def confirm_is_annotated(self):
        """Move Sample object from presample to sample endpoint."""
        if self.endpoint == 'presample':
            self.api(self.id).patch({'presample': False})
            self.logger.info('Moved Sample %s from presmaples to samples', self.id)
        else:
            raise NotImplementedError("Method supports objects in presample endpoint only.")
