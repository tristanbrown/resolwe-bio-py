"""Collection"""
from __future__ import absolute_import, division, print_function, unicode_literals


class Collection(object):

    """Resolwe collection annotation."""

    def __init__(self, data, resolwe):
        for field in data:
            setattr(self, field, data[field])

        self.resolwe = resolwe
        self.id = getattr(self, 'id', None)  # pylint: disable=invalid-name
        self.name = getattr(self, 'name', None)

    def data_types(self):
        """Return a list of data types."""
        data = self.resolwe.project_data(self.id)
        return sorted(set(d.type for d in data))

    def data(self, **query):
        """Query for Data object annotation."""
        data = self.resolwe.project_data(self.id)
        query['case_ids__contains'] = self.id
        ids = set(d['id'] for d in self.resolwe.api.dataid.get(**query)['objects'])
        return [d for d in data if d.id in ids]

    def find(self, filter_str):
        """Filter Data object annotation."""
        raise NotImplementedError()

    def __str__(self):
        return self.name or 'n/a'

    def __repr__(self):
        return u"Collection: {} - {}".format(self.id, self.name)
