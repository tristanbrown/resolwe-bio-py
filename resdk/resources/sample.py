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

    def __init__(self, slug=None, id=None, model_data=None,  # pylint: disable=redefined-builtin
                 resolwe=None):
        """Initialize attributes."""
        super(Sample, self).__init__(slug, id, model_data, resolwe)

        #: (lazy loaded) list of collections  to which object belongs
        self.collections = self.resolwe.collection.filter(entity=self.id)
        #: (lazy loaded) list of data object that belong to sample
        self.data = self.resolwe.data.filter(entity=self.id)

    def update(self):
        """Clear cache and update resource fields from the server."""
        self.collections.clear_cache()
        self.data.clear_cache()  # pylint: disable=no-member

        super(Sample, self).update()

    def _clear_data_cache(self):
        self.data.clear_cache()  # pylint: disable=no-member

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
