"""Sample resource."""
from __future__ import absolute_import, division, print_function, unicode_literals

from .collection import BaseCollection


class SampleUtilsMixin(object):
    """Mixin with utility functions for `~resdk.resources.sample.Sample` resource.

    This mixin includes handy methods for common tasks like getting
    data object of specific type from sample (or list of them, based on
    common usecase) and running analysis on the objects in the sample.

    """

    def get_reads(self):
        """Return ``fastq`` object on the sample."""
        return self.data.get(type='data:reads:fastq')

    def get_bam(self):
        """Return ``bam`` object on the sample."""
        return self.data.get(type='data:alignment:bam')

    def get_primary_bam(self, fallback_to_bam=False):
        """Return ``primary bam`` object on the sample.

        If the ``primary bam`` object is not present and
        ``fallback_to_bam`` is set to ``True``, a ``bam`` object will
        be returned.

        """
        try:
            return self.data.get(type='data:alignment:bam:primary')
        except LookupError:
            if fallback_to_bam:
                return self.get_bam()
            else:
                raise

    def get_macs(self):
        """Return list of ``bed`` objects on the sample."""
        return self.data.filter(type='data:chipseq:macs14')

    def get_cuffquant(self):
        """Return ``cuffquant`` object on the sample."""
        return self.data.get(type='data:cufflinks:cuffquant')

    def get_expression(self):
        """Return ``expression`` object on the sample."""
        return self.data.get(type='data:expression:')


class Sample(SampleUtilsMixin, BaseCollection):
    """Resolwe Sample resource.

    One and only one of the identifiers (slug, id or model_data)
    should be given.

    :param resolwe: Resolwe instance
    :type resolwe: Resolwe object
    :param model_data: Resource model data

    """

    endpoint = 'sample'

    WRITABLE_FIELDS = ('tags',) + BaseCollection.WRITABLE_FIELDS

    #: (lazy loaded) list of collections  to which object belongs
    _collections = None

    def __init__(self, resolwe, **model_data):
        """Initialize attributes."""
        #: sample's tags
        self.tags = None

        super(Sample, self).__init__(resolwe, **model_data)

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
        self.descriptor = descriptor

    def confirm_is_annotated(self):
        """Mark sample as annotated (descriptor is completed)."""
        self.api(self.id).patch({'descriptor_completed': True})
        self.logger.info('Marked Sample %s as annotated', self.id)

    def get_background(self, fail_silently=False, **extra_filters):
        """Find background sample of the current one."""
        background_relation = self.resolwe.relation.filter(
            type='compare',
            label='background',
            entity=[self.id],
            position=['sample'],
            **extra_filters
        )

        # Execute query to prevent multiple requests to api
        background_relation = list(background_relation)

        if len(background_relation) > 1:
            raise LookupError(
                "More than one background is defined for sample '{}'".format(self.name)
            )
        elif len(background_relation) == 1:
            for entity_obj in background_relation[0].entities:
                if entity_obj['position'] == 'background':
                    return self.resolwe.sample.get(id=entity_obj['entity'])
        elif not fail_silently:
            raise LookupError(
                'Cannot find (background) sample for sample `{}`.'.format(self.name))
