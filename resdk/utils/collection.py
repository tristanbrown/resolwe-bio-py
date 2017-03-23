"""Collection utils."""
from __future__ import absolute_import, division, print_function, unicode_literals


class CollectionUtilsMixin(object):
    """Mixin with utility functions for `~resdk.resources.collection.Colleciton` resource.

    This mixin includes handy methods for common tasks like running
    analysis on the data objects and samples in the sample.

    """

    def run_macs(self, use_background=True, p_value=None):
        """Run macs on samples in collection."""
        if use_background:
            for relation in self.relations.filter(type='compare', label='background'):
                for entity_obj in relation.entities:
                    if entity_obj['position'] == 'sample':
                        sample = self.resolwe.sample.get(entity_obj['entity'])
                sample.run_macs(use_background=True, p_value=p_value)
        else:
            for sample in self.samples.all():
                sample.rum_macs(use_background=False, p_value=p_value)
