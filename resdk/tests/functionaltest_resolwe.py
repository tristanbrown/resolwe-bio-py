"""
Some simple functional tests.
"""
# pylint: disable=missing-docstring

import os
import unittest
import six

import resdk
from resdk.resources import Data, Sample, Collection


EMAIL = 'admin'
PASSW = 'admin'
URL = 'http://127.0.0.1:8000/'
# Set test data IDs. The test data should exist on Resolwe server.
SAMPLE_ID = 25
COLLECTION_ID = 10
DATA_ID = 42


class TestResolwe(unittest.TestCase):

    def test_resolwe(self):

        # Test authentication
        resolwe = resdk.Resolwe(EMAIL, PASSW, URL)

        # Test_processes:
        processes = resolwe.processes()
        self.assertIsInstance(processes, list)
        self.assertTrue(len(processes) > 10)
        upload_process = resolwe.processes('Upload NGS reads')
        self.assertIsInstance(upload_process, list)
        self.assertIsInstance(upload_process[0], dict)


class TestResolweQuerry(unittest.TestCase):

    def test_get_and_filter(self):

        # Test authentication
        resolwe = resdk.Resolwe(EMAIL, PASSW, URL)

        # Test get
        data = resolwe.data.get(DATA_ID)
        self.assertIsInstance(data, Data)
        sample = resolwe.sample.get(SAMPLE_ID)
        self.assertIsInstance(sample, Sample)
        collection = resolwe.collection.get(COLLECTION_ID)
        self.assertIsInstance(collection, Collection)

        # Test filter
        data = resolwe.data.filter(status="OK")
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], Data)
        samples = resolwe.sample.filter(contributor=1)
        self.assertIsInstance(samples, list)
        self.assertIsInstance(samples[0], Sample)
        collections = resolwe.collection.filter(data=DATA_ID)
        self.assertIsInstance(collections, list)
        self.assertIsInstance(collections[0], Collection)


class TestFilesAndDownload(unittest.TestCase):

    def test_files(self):
        # Test authentication
        resolwe = resdk.Resolwe(EMAIL, PASSW, URL)
        sample = resolwe.sample.get(SAMPLE_ID)

        # Test files() function:
        flist = sample.files()
        self.assertIsInstance(flist, list)
        self.assertTrue(len(flist) >= 1)
        self.assertIsInstance(flist[0], six.string_types)

        flist = sample.files(verbose=True)
        self.assertIsInstance(flist, list)
        self.assertTrue(len(flist) >= 1)
        self.assertIsInstance(flist[0], tuple)
        self.assertEqual(len(flist[0]), 4)

    def test_download(self):
        # Test authentication
        resolwe = resdk.Resolwe(EMAIL, PASSW, URL)
        sample = resolwe.sample.get(SAMPLE_ID)

        all_files = sample.files()

        # Test download() function - no params:
        sample.download()

        # Check if file has bee downloaded
        for fname in all_files:
            self.assertTrue(os.path.isfile(fname))
            # Then clean up = remove file
            os.remove(fname)

        # Test download() function - param name:
        fname = all_files[0]
        sample.download(name=fname)
        self.assertTrue(os.path.isfile(fname))
        self.assertFalse(os.path.isfile(all_files[1]))
        os.remove(fname)

        # Test download() function - param typ as tuple:
        sample.download(type=('data:reads:fastq:', 'output.fastq'))
        self.assertTrue(os.path.isfile(fname))
        self.assertFalse(os.path.isfile(all_files[1]))
        os.remove(fname)

        # Test download() function - param typ as abbreviation string:
        sample.download(type='fastq')
        self.assertTrue(os.path.isfile(fname))
        self.assertFalse(os.path.isfile(all_files[1]))
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
