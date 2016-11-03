"""
Unit tests for resdk/resources/utils.py file.
"""
# pylint: disable=missing-docstring, protected-access

import unittest

import six

from mock import MagicMock, patch, call

from resdk.resources import Collection, Data, Sample, Process
from resdk.resources.utils import (
    _print_input_line, endswith_colon, iterate_fields, iterate_schema, find_field, fill_spaces,
    get_collection_id, get_data_id, get_sample_id, get_process_id)


PROCESS_OUTPUT_SCHEMA = [
    {'name': "fastq", 'type': "basic:file:", 'label': "Reads file"},
    {'name': "bases", 'type': "basic:string:", 'label': "Number of bases"},
    {'name': "options", 'label': "Options", 'group': [
        {'name': "id", 'type': "basic:string:", 'label': "ID"},
        {'name': "k", 'type': "basic:integer:", 'label': "k-mer size"}
    ]}
]

OUTPUT = {
    'fastq': {'file': "example.fastq.gz"},
    'bases': "75",
    'options': {
        'id': 'abc',
        'k': 123}
}


class TestUtils(unittest.TestCase):

    def test_iterate_fields(self):
        result = list(iterate_fields(OUTPUT, PROCESS_OUTPUT_SCHEMA))
        # result object is iterator - we use lists to pull all elements

        expected = [
            ({
                'type': 'basic:string:',
                'name': 'id',
                'label': 'ID'
            }, {
                'k': 123,
                'id': 'abc'
            }), ({
                'type': 'basic:string:',
                'name': 'bases',
                'label': 'Number of bases'
            }, {
                'options': {
                    'k': 123,
                    'id': 'abc'
                },
                'bases': '75',
                'fastq': {
                    'file': 'example.fastq.gz'
                }
            }), ({
                'type': 'basic:file:',
                'name': 'fastq',
                'label': 'Reads file'
            }, {
                'options': {
                    'k': 123,
                    'id': 'abc'
                },
                'bases': '75',
                'fastq': {
                    'file': 'example.fastq.gz'
                }
            }), ({
                'type': 'basic:integer:',
                'name': 'k',
                'label': 'k-mer size'
            }, {
                'k': 123,
                'id': 'abc'
            })
        ]

        six.assertCountEqual(self, result, expected)

    def test_iterate_fields_modif(self):
        """
        Ensure that changing ``values`` inside iteration loop also changes ``OUTPUT`` values.
        """
        for schema, values in iterate_fields(OUTPUT, PROCESS_OUTPUT_SCHEMA):
            field_name = schema['name']
            if field_name == "bases":
                values[field_name] = str(int(values[field_name]) + 1)

        self.assertEqual(OUTPUT['bases'], "76")
        # Fix the OUTPUT to previous state:
        OUTPUT['bases'] = "75"

    def test_find_field(self):
        result = find_field(PROCESS_OUTPUT_SCHEMA, 'fastq')

        expected = {'type': 'basic:file:', 'name': 'fastq', 'label': 'Reads file'}

        self.assertEqual(result, expected)

    def test_iterate_schema(self):
        result1 = list(iterate_schema(OUTPUT, PROCESS_OUTPUT_SCHEMA, 'my_path'))
        result2 = list(iterate_schema(OUTPUT, PROCESS_OUTPUT_SCHEMA))

        expected1 = [
            ({'name': 'fastq', 'label': 'Reads file', 'type': 'basic:file:'},
             {'fastq': {'file': 'example.fastq.gz'}, 'options': {'k': 123, 'id': 'abc'},
              'bases': '75'}, 'my_path.fastq'),

            ({'name': 'bases', 'label': 'Number of bases', 'type': 'basic:string:'},
             {'fastq': {'file': 'example.fastq.gz'}, 'options': {'k': 123, 'id': 'abc'},
              'bases': '75'}, 'my_path.bases'),

            ({'name': 'id', 'label': 'ID', 'type': 'basic:string:'}, {'k': 123, 'id': 'abc'},
             'my_path.options.id'),

            ({'name': 'k', 'label': 'k-mer size', 'type': 'basic:integer:'},
             {'k': 123, 'id': 'abc'}, 'my_path.options.k')]

        expected2 = [
            ({'type': 'basic:file:', 'name': 'fastq', 'label': 'Reads file'},
             {'fastq': {'file': 'example.fastq.gz'}, 'bases': '75',
              'options': {'k': 123, 'id': 'abc'}}),

            ({'type': 'basic:string:', 'name': 'bases', 'label': 'Number of bases'},
             {'fastq': {'file': 'example.fastq.gz'}, 'bases': '75',
              'options': {'k': 123, 'id': 'abc'}}),

            ({'type': 'basic:string:', 'name': 'id', 'label': 'ID'}, {'k': 123, 'id': 'abc'}),

            ({'type': 'basic:integer:', 'name': 'k', 'label': 'k-mer size'},
             {'k': 123, 'id': 'abc'})]

        self.assertEqual(result1, expected1)
        self.assertEqual(result2, expected2)

    def test_fill_spaces(self):
        result = fill_spaces("one_word", 12)
        self.assertEqual(result, "one_word    ")

    @patch('resdk.resources.utils.print')
    def test_print_input_line(self, print_mock):
        _print_input_line(PROCESS_OUTPUT_SCHEMA, 0)
        calls = [
            call(u'- fastq     [basic:file:]   - Reads file'),
            call(u'- bases     [basic:string:] - Number of bases'),
            call(u'- options - Options'),
            call(u'    - id   [basic:string:]  - ID'),
            call(u'    - k    [basic:integer:] - k-mer size')]

        self.assertEqual(print_mock.mock_calls, calls)

    def test_endswith_colon(self):

        schema = {'process_type': 'data:reads:fastq:single'}

        endswith_colon(schema, 'process_type')

        self.assertEqual(schema, {'process_type': u'data:reads:fastq:single:'})

    def test_get_collection_id(self):
        collection = Collection(id=1, resolwe=MagicMock())
        collection.id = 1  # this is overriden when initialized
        self.assertEqual(get_collection_id(collection), 1)

        self.assertEqual(get_collection_id(2), 2)

    def test_get_sample_id(self):
        sample = Sample(id=1, resolwe=MagicMock())
        sample.id = 1  # this is overriden when initialized
        self.assertEqual(get_sample_id(sample), 1)

        self.assertEqual(get_sample_id(2), 2)

    def test_get_data_id(self):
        data = Data(id=1, resolwe=MagicMock())
        data.id = 1  # this is overriden when initialized
        self.assertEqual(get_data_id(data), 1)

        self.assertEqual(get_data_id(2), 2)

    def test_get_process_id(self):
        process = Process(id=1, resolwe=MagicMock())
        process.id = 1  # this is overriden when initialized
        self.assertEqual(get_process_id(process), 1)

        self.assertEqual(get_process_id(2), 2)


if __name__ == '__main__':
    unittest.main()
