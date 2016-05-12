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
        # Prepare id's
        SAMPLE_ID = int(resolwe.sample.filter()[0].id)
        COLLECTION_ID = int(resolwe.collection.filter()[0].id)
        DATA_ID = int(resolwe.collection.filter()[0].data[0])

        # Test get
        d = resolwe.data.get(DATA_ID)
        self.assertIsInstance(d, Data)
        d = resolwe.sample.get(SAMPLE_ID)
        self.assertIsInstance(d, Sample)
        d = resolwe.collection.get(COLLECTION_ID)
        self.assertIsInstance(d, Collection)

        # Test filter
        d = resolwe.data.filter(status="OK")
        self.assertIsInstance(d, list)
        self.assertIsInstance(d[0], Data)
        d = resolwe.sample.filter(contributor=1)
        self.assertIsInstance(d, list)
        self.assertIsInstance(d[0], Sample)
        d = resolwe.collection.filter(data=DATA_ID)
        self.assertIsInstance(d, list)
        self.assertIsInstance(d[0], Collection)


class TestFilesAndDownload(unittest.TestCase):

    def test_files(self):

        # Test authentication
        resolwe = resdk.Resolwe(EMAIL, PASSW, URL)
        # SAMPLE_ID = int(resolwe.sample.filter()[0].id)
        # Pick sample id, where sample has some data in sample.data field
        SAMPLE_ID = 25

        s = resolwe.sample.get(SAMPLE_ID)

        # Test files() function:
        flist = s.files()
        self.assertIsInstance(flist, list)
        self.assertTrue(len(flist) >= 1)
        self.assertIsInstance(flist[0], six.string_types)

        flist = s.files(verbose=True)
        self.assertIsInstance(flist, list)
        self.assertTrue(len(flist) >= 1)
        self.assertIsInstance(flist[0], tuple)
        self.assertEqual(len(flist[0]), 4)

    def test_download(self):

        # Test authentication
        resolwe = resdk.Resolwe(EMAIL, PASSW, URL)
        # SAMPLE_ID = int(resolwe.sample.filter()[0].id)
        # Pick sample id, where sample has some data in sample.data field
        SAMPLE_ID = 25

        s = resolwe.sample.get(SAMPLE_ID)
        all_files = s.files()

        # Test download() function - no params:
        s.download()
        # Check if file has bee downloaded
        for f in all_files:
            self.assertTrue(os.path.isfile(f))
            # Then clean up = remove file
            os.remove(f)

        # Test download() function - param name:
        fname = all_files[0]
        s.download(name=fname)
        self.assertTrue(os.path.isfile(fname))
        self.assertFalse(os.path.isfile(all_files[1]))
        os.remove(fname)

        # Test download() function - param typ as tuple:
        s.download(typ=('data:reads:fastq:', 'output.fastq'))
        self.assertTrue(os.path.isfile(fname))
        self.assertFalse(os.path.isfile(all_files[1]))
        os.remove(fname)

        # Test download() function - param typ as abbreviation string:
        s.download(typ='fastq')
        self.assertTrue(os.path.isfile(fname))
        self.assertFalse(os.path.isfile(all_files[1]))
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
