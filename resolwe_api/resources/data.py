"""Data"""
from __future__ import absolute_import, division, print_function, unicode_literals

from .utils import iterate_schema


class Data(object):

    endpoint = 'data'

    """
    Resolwe data object annotation.
    """

    def __init__(self, data, resolwe):
        self.resolwe = resolwe
        self.update(data)

    def update(self, data):
        """
        Update the object with new data.

        :param data: Annotation data for data object
        :type collection: dictionary

        :rtype: None

        """

        fields = [
            'slug',
            'name',
            'contributor',
            'input',
            'output',
            'descriptor_schema',
            'descriptor',
            'process',
            'id',
            'created',
            'modified',
            'started',
            'finished',
            'checksum',
            'status',
            'process_progress',
            'process_rc',
            'process_info',
            'process_warning',
            'process_error',
            'process_type',
            'process_input_schema',
            'process_output_schema',
            'process_name',
            'permissions',
        ]

        self.annotation = {}
        for f in fields:
            setattr(self, f, data[f])

        self.annotation.update(self._flatten_field(data['input'],
                                                   data['process_input_schema'],
                                                   'input'
                                                   )
                               )
        self.annotation.update(self._flatten_field(data['output'],
                                                   data['process_output_schema'],
                                                   'output'
                                                   )
                               )

    def _flatten_field(self, field, schema, path):
        """
        Reduce dicts of dicts to dot separated keys.

        :param field: Field instance (e.g. input)
        :type field: dict
        :param schema: Schema instance (e.g. input_schema)
        :type schema: dict
        :param path: Field path
        :type path: string
        :return: flattened annotations
        :rtype: dictionary
        """
        flat = {}
        for field_schema, fields, path in iterate_schema(field, schema, path):
            name = field_schema['name']
            typ = field_schema['type']
            label = field_schema['label']
            value = fields[name] if name in fields else None
            flat[path] = {'name': name, 'value': value, 'type': typ, 'label': label}

        return flat

    def print_annotation(self):
        """Print "key: value" pairs to standard output."""
        for path, ann in self.annotation.items():
            print("{}: {}".format(path, ann['value']))

    def _get_download_list(self, verbose=False):
        """
        Get list of all downloadable fields

        :param verbose: Verbose output.
        :type verbose: boolean

        If verbose = False, return list of strings (file names)
        If verbose = True, return list of tuples. Each tuple contains:
        (data_id, file_name, field_name, process_type)
        """
        dlist = []
        for path, ann in self.annotation.items():
            if path.startswith('output') and ann['type'] == 'basic:file:':
                if verbose:
                    dlist.append((self.id,
                                 ann['value']['file'],
                                 path,
                                 self.process_type)
                                 )
                else:
                    dlist.append(ann['value']['file'])
        return dlist

    def print_downloads(self):
        """Print fields that can be downloaded to standard output."""
        for path, ann in self.annotation.items():
            if path.startswith('output') and ann['type'] == 'basic:file:':
                print("{}: {}".format(path, ann['value']['file']))

    def download(self, field):
        """Download a file.

        :param field: file field to download
        :type field: string
        :rtype: a file handle

        """
        if not field.startswith('output'):
            raise ValueError("Only processor results (output.* fields) can be downloaded")

        if field not in self.annotation:
            raise ValueError("Download field {} does not exist".format(field))

        ann = self.annotation[field]
        if ann['type'] != 'basic:file:':
            raise ValueError("Only basic:file: field can be downloaded")

        return next(self.resolwe.download([self.id], field))

    def __str__(self):
        return self.name

    def __repr__(self):
        return u"Data: {} - {}".format(self.id, self.name)
