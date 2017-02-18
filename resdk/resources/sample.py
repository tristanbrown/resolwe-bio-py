"""Sample resource."""
from __future__ import absolute_import, division, print_function, unicode_literals

from resdk.utils.sample import SampleUtilsMixin

from .collection import BaseCollection


class Sample(SampleUtilsMixin, BaseCollection):
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

    #: (lazy loaded) list of collections  to which object belongs
    _collections = None

    def __init__(self, slug=None, id=None, model_data=None,  # pylint: disable=redefined-builtin
                 resolwe=None):
        """Initialize attributes."""
        super(Sample, self).__init__(slug, id, model_data, resolwe)

    def update(self):
        """Clear cache and update resource fields from the server."""
        self._collections = None
        self._data = None

        super(Sample, self).update()

    @property
    def data(self):
        """Return list of data objects on collection."""
        if self.id is None:
            raise ValueError('Instance must be saved before accessing `data` attribute.')
        if self._data is None:
            self._data = self.resolwe.data.filter(entity=self.id)

        return self._data

    @property
    def collections(self):
        """Return list of collections to which sample belongs."""
        if self.id is None:
            raise ValueError('Instance must be saved before accessing `collections` attribute.')
        if self._collections is None:
            self._collections = self.resolwe.collection.filter(entity=self.id)

        return self._collections

    def print_annotation(self):
        """Provide annotation data."""
        raise NotImplementedError()

    def update_descriptor(self, descriptor):
        """Update descriptor and descriptor_schema."""
        self.api(self.id).patch({'descriptor': descriptor})

    def confirm_is_annotated(self):
        """Mark sample as annotated (descriptor is completed)."""
        self.api(self.id).patch({'descriptor_completed': True})
        self.logger.info('Marked Sample %s as annotated', self.id)

    def get_background(self, background_slug, fail_silently=False):
        """Find background sample of the current one."""
        # XXX: This is a workaround until relations are implemented in the right way.

        if not background_slug and fail_silently:
            return None

        try:
            return self.resolwe.sample.get(slug=background_slug)
        except LookupError:
            raise LookupError(
                'Cannot find (background) sample with slug `{}`.'.format(background_slug))
