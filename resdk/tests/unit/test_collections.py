"""
Unit tests for resdk/resources/collection.py file.
"""
# pylint: disable=missing-docstring, protected-access

import unittest

import six

from mock import patch, MagicMock

from resdk.resources.collection import BaseCollection, Collection
from resdk.resources.sample import Sample
from resdk.tests.mocks.data import DATA_SAMPLE

DATA0 = MagicMock(**{'files.return_value': [], 'id': 0})

DATA1 = MagicMock(**{'files.return_value': ['reads.fq', 'arch.gz'], 'id': 1})

DATA2 = MagicMock(**{'files.return_value': ['outfile.exp'], 'id': 2})


class TestBaseCollection(unittest.TestCase):

    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_data_types(self, collection_mock):
        get_mock = MagicMock(**{'get.return_value': DATA_SAMPLE[0]})
        api_mock = MagicMock(**{'data.return_value': get_mock})
        collection_mock.configure_mock(data=[1, 2], resolwe=MagicMock(api=api_mock))

        types = BaseCollection.data_types(collection_mock)
        self.assertEqual(types, [u'data:reads:fastq:single:'])

    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_files(self, collection_mock):
        collection_mock.configure_mock(data=[DATA1, DATA2], resolwe=" ")

        flist = BaseCollection.files(collection_mock)
        self.assertEqual(set(flist), set(['arch.gz', 'reads.fq', 'outfile.exp']))

    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_print_annotation(self, collection_mock):
        with self.assertRaises(NotImplementedError):
            BaseCollection.print_annotation(collection_mock)


class TestBaseCollectionDownload(unittest.TestCase):

    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_file_type(self, collection_mock):
        collection_mock.configure_mock(data=[DATA0, DATA2], resolwe=MagicMock())
        BaseCollection.download(collection_mock, file_type='output.exp')
        flist = [u'2/outfile.exp']
        collection_mock.resolwe._download_files.assert_called_once_with(flist, None)

        # Check if ok to also provide ``output_field`` that does not start with 'output'
        collection_mock.reset_mock()
        collection_mock.configure_mock(data=[DATA1, DATA0], resolwe=MagicMock())
        BaseCollection.download(collection_mock, file_type='fastq')
        flist = [u'1/reads.fq', u'1/arch.gz']
        collection_mock.resolwe._download_files.assert_called_once_with(flist, None)

    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_bad_file_type(self, collection_mock):
        message = "Invalid argument value `file_type`."
        with six.assertRaisesRegex(self, ValueError, message):
            BaseCollection.download(collection_mock, file_type=123)


class TestCollection(unittest.TestCase):

    @patch('resdk.resources.collection.Collection', spec=True)
    def test_collection_print_ann(self, collection_mock):
        with self.assertRaises(NotImplementedError):
            Collection.print_annotation(collection_mock)

    def test_data(self):
        resolwe_mock = MagicMock(**{'data.filter.return_value': ['data_1', 'data_2', 'data_3']})
        collection = Collection(id=1, resolwe=resolwe_mock)

        self.assertEqual(collection.data, ['data_1', 'data_2', 'data_3'])

        # cache is cleared at update
        collection.data = MagicMock()
        collection.update()
        self.assertEqual(collection.data.clear_cache.call_count, 1)

    def test_samples(self):
        resolwe_mock = MagicMock(**{'sample.filter.return_value': ['sample1', 'sample2']})
        collection = Collection(id=1, resolwe=resolwe_mock)

        self.assertEqual(collection.samples, ['sample1', 'sample2'])

        # cache is cleared at update
        collection.samples = MagicMock()
        collection.update()
        self.assertEqual(collection.samples.clear_cache.call_count, 1)


class TestSample(unittest.TestCase):

    def test_data(self):
        resolwe_mock = MagicMock(**{'data.filter.return_value': ['data_1', 'data_2', 'data_3']})
        sample = Sample(id=1, resolwe=resolwe_mock)

        self.assertEqual(sample.data, ['data_1', 'data_2', 'data_3'])

        # cache is cleared at update
        sample.data = MagicMock()
        sample.update()
        self.assertEqual(sample.data.clear_cache.call_count, 1)

    def test_collections(self):
        resolwe_mock = MagicMock(
            **{'collection.filter.return_value': ['collection_1', 'collection_2']})
        sample = Sample(id=1, resolwe=resolwe_mock)

        self.assertEqual(sample.collections, ['collection_1', 'collection_2'])

        # cache is cleared at update
        sample.collections = MagicMock()
        sample.update()
        self.assertEqual(sample.collections.clear_cache.call_count, 1)

    @patch('resdk.resources.sample.Sample', spec=True)
    def test_sample_print_annotation(self, sample_mock):
        with self.assertRaises(NotImplementedError):
            Sample.print_annotation(sample_mock)

    @patch('resdk.resources.sample.Sample', spec=True)
    def test_update_descriptor(self, sample_mock):
        sample_mock.configure_mock(id=42, api=MagicMock())
        Sample.update_descriptor(sample_mock, {'field': 'value'})
        sample_mock.api(42).patch.assert_called_once_with({u'descriptor': {'field': 'value'}})

    @patch('resdk.resources.sample.Sample', spec=True)
    def test_confirm_is_annotated(self, sample_mock):
        sample_mock.configure_mock(endpoint='anything but presample')
        with self.assertRaises(NotImplementedError):
            Sample.confirm_is_annotated(sample_mock)

        sample_mock.configure_mock(endpoint='presample', id=42,
                                   api=MagicMock(), logger=MagicMock())
        Sample.confirm_is_annotated(sample_mock)
        sample_mock.api(42).patch.assert_called_once_with({'presample': False})


if __name__ == '__main__':
    unittest.main()
