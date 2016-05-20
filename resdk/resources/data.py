"""Data"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import requests

from six.moves.urllib.parse import urljoin  # pylint: disable=import-error

from .utils import iterate_schema
from .base import BaseResource


class Data(BaseResource):
    """
    Resolwe Data resource.
    """

    endpoint = 'data'

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None):
        """
        Resolwe Data resource.

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
        self.status = None
        self.input = None
        self.process_type = None

        BaseResource.__init__(self, slug, id, model_data, resolwe)

        self.logger = logging.getLogger(__name__)

    def _update_fields(self, fields):
        """
        Update the Data object with new data.

        :param fields: Data resource fields
        :type fields: dict

        :rtype: None
        """
        BaseResource._update_fields(self, fields)

        self.annotation = {}
        self.annotation.update(
            self._flatten_field(fields['input'], fields['process_input_schema'], 'input'))

        self.annotation.update(
            self._flatten_field(fields['output'], fields['process_output_schema'], 'output'))

        # TODO Descriptor schema!

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

    def files(self, file_name=None, field_name=None):
        """
        Get list of downloadable fields.

        Filter files by file name or output field.

        :param file_name: name of file
        :type file_name: string
        :param field_name: output field name
        :type field_name: string
        :rtype: List of tuples (data_id, file_name, field_name, process_type)

        """
        download_list = []
        for file_field_name, ann in self.annotation.items():
            if (file_field_name.startswith('output') and
                    ann['type'].startswith('basic:file:') and
                    ann['value'] is not None and
                    (file_name is None or file_name == ann['value']['file']) and
                    (field_name is None or field_name == file_field_name)):

                download_list.append(ann['value']['file'])

        return download_list

    def download(self, file_name=None, field_name=None, download_dir=None):
        """
        Download Data object's files.

        Download files from the Resolwe server to the download
        directory (defaults to the current working directory).

        :param file_name: name of file
        :type file_name: string
        :param field_name: file field name
        :type field_name: string
        :param download_dir: download path
        :type download_dir: string
        :rtype: None

        Data objects can contain multiple files. All are downloaded by
        default, but may be filtered by name or output field:

        * re.data.get(42).download(file_name='alignment7.bam')
        * re.data.get(42).download(field_name='bam')

        """
        if file_name and field_name:
            raise ValueError("Only one of file_name or field_name may be given")

        files = ['{}/{}'.format(self.id, fname) for fname in self.files(file_name, field_name)]
        self.resolwe.download_files(files, download_dir)

    def print_annotation(self):
        """
        Provide annotation data.
        """
        # TODO: Think of neat way to present all annotation. how this would be most neatly presented...
        raise NotImplementedError()

    def stdout(self):
        """
        Return process standard output (stdout.txt file content).

        Fetch a stdout.txt file of the corresponding Data object form
        the Resolwe server and return the file content as a string. The
        string can be long and ugly.

        :rtype: string

        """
        output = ''
        try:
            url = urljoin(self.resolwe.url, 'data/{}/stdout.txt'.format(self.id))
            response = requests.get(url, stream=True, auth=self.resolwe.auth)
            if not response.ok:
                response.raise_for_status()
            else:
                for chunk in response:
                    output += chunk
        except requests.exceptions.HTTPError as http_error:
            raise http_error

        return output
