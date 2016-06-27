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

DATA1 = MagicMock(
    process_type="data:reads:fastq:single:", **{'files.return_value': ['reads.fq', 'arch.gz']})

DATA2 = MagicMock(
    process_type='data:expression:blah',
    **{'files.return_value': ['outfile.exp']})


class TestBaseCollection(unittest.TestCase):

    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_init(self, collection_mock):
        collection_mock.configure_mock(endpoint="fake_endpoint")
        BaseCollection.__init__(collection_mock, id=1, resolwe=MagicMock())

    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_data_types(self, collection_mock):
        api_mock = MagicMock(**{'data.return_value': MagicMock(**{'get.return_value': DATA_SAMPLE[0]})})
        collection_mock.configure_mock(data=[1, 2], resolwe=MagicMock(api=api_mock))

        types = BaseCollection.data_types(collection_mock)
        self.assertEqual(types, [u'data:reads:fastq:single:'])

    @patch('resdk.resources.collection.Data')
    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_files(self, collection_mock, data_mock):
        collection_mock.configure_mock(data=[1, 2], resolwe=" ")
        data_mock.side_effect = [DATA1, DATA2]

        flist = BaseCollection.files(collection_mock)
        self.assertEqual(set(flist), set(['arch.gz', 'reads.fq', 'outfile.exp']))

    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_print_annotation(self, collection_mock):
        with self.assertRaises(NotImplementedError):
            BaseCollection.print_annotation(collection_mock)


class TestBaseCollectionDownload(unittest.TestCase):

    @patch('resdk.resources.collection.Data')
    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_data_type_short(self, collection_mock, data_mock):
        collection_mock.configure_mock(data=[1, 2], resolwe=MagicMock())
        data_mock.side_effect = [DATA1, DATA2]

        BaseCollection.download(collection_mock, data_type='fastq')
        flist = [u'1/reads.fq', u'1/arch.gz']
        collection_mock.resolwe.download_files.assert_called_once_with(flist, None)

    @patch('resdk.resources.collection.Data')
    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_data_type_tuple(self, collection_mock, data_mock):
        collection_mock.configure_mock(data=[1, 2], resolwe=MagicMock())
        data_mock.side_effect = [DATA1, DATA2, DATA1, DATA2]

        BaseCollection.download(collection_mock, data_type=('data:expression:', 'output.exp'))
        flist = [u'2/outfile.exp']
        collection_mock.resolwe.download_files.assert_called_once_with(flist, None)

        # Check if ok to also provide ``output_field`` that does not start with 'output'
        collection_mock.reset_mock()
        BaseCollection.download(collection_mock, data_type=('data:expression:', 'exp'))
        collection_mock.resolwe.download_files.assert_called_once_with(flist, None)

    @patch('resdk.resources.collection.Data')
    @patch('resdk.resources.collection.BaseCollection', spec=True)
    def test_bad_data_type(self, collection_mock, data_mock):
        message = "Invalid argument value data_type."
        with six.assertRaisesRegex(self, ValueError, message):
            BaseCollection.download(collection_mock, data_type=123)


class TestCollection(unittest.TestCase):

    @patch('resdk.resources.collection.Collection', spec=True)
    def test_collection_init(self, collection_mock):
        collection_mock.configure_mock(endpoint="fake_endpoint")
        Collection.__init__(collection_mock, id=1, resolwe=MagicMock())

    @patch('resdk.resources.collection.Collection', spec=True)
    def test_collection_print_ann(self, collection_mock):
        with self.assertRaises(NotImplementedError):
            Collection.print_annotation(collection_mock)


class TestSample(unittest.TestCase):

    @patch('resdk.resources.sample.Sample', spec=True)
    def test_sample_init(self, sample_mock):
        sample_mock.configure_mock(endpoint="fake_endpoint")
        Sample.__init__(sample_mock, id=1, resolwe=MagicMock())

    @patch('resdk.resources.sample.Sample', spec=True)
    def test_sample_print_annotation(self, sample_mock):
        with self.assertRaises(NotImplementedError):
            Sample.print_annotation(sample_mock)

if __name__ == '__main__':
    unittest.main()
