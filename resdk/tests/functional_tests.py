"""
Some simple functional tests.
"""
# pylint: disable=missing-docstring

import os
import unittest

import resdk


class UserTest(unittest.TestCase):

    def test_user_story(self):

        # Test authentication
        email = 'admin'
        passw = 'admin'
        url = 'http://127.0.0.1:8000/'
        resolwe = resdk.Resolwe(email, passw, url)

        # Test_processes:
        processes = resolwe.processes()
        self.assertIsInstance(processes, list)
        self.assertTrue(len(processes) > 10)
        upload_process = resolwe.processes('Upload NGS reads')
        self.assertIsInstance(upload_process, list)
        self.assertIsInstance(upload_process[0], dict)

        # Test upload (consequently also _upload_file & create)
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files', 'example.fastq')
        resolwe.run('import-upload-reads-fastq', input={'src': fn}, collections=[1], data_name='name_abc')


if __name__ == '__main__':
    unittest.main()
