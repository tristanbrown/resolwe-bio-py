"""
Unit tests for resdk/resolwe.py file.
"""
# pylint: disable=missing-docstring, protected-access

import os
import unittest
import six

from mock import patch, MagicMock
import requests
from slumber.exceptions import HttpNotFoundError

from resdk.resolwe import Resolwe, ResAuth
from resdk.tests.mocks.data import PROCESS_SAMPLE, DATA_SAMPLE

if six.PY2:
    # pylint: disable=deprecated-method
    unittest.TestCase.assertRegex = unittest.TestCase.assertRegexpMatches


class TestResolweProcesses(unittest.TestCase):

    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_process_without_name(self, resolwe_mock):
        resolwe_mock.api = MagicMock()
        resolwe_mock.api.process.get = MagicMock(return_value=PROCESS_SAMPLE)

        resolwe = Resolwe.processes(resolwe_mock)

        self.assertIsInstance(resolwe, list)
        self.assertEqual(len(resolwe), 4)
        self.assertIsInstance(resolwe[0], dict)
        self.assertEqual(resolwe[0]['name'], 'Upload NGS reads')
        self.assertEqual(len(resolwe_mock.api.mock_calls), 1)

    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_process_with_process_name(self, resolwe_mock):
        resolwe_mock.api = MagicMock()
        resolwe_mock.api.process.get = MagicMock(return_value=PROCESS_SAMPLE)

        resolwe = Resolwe.processes(resolwe_mock, 'Variant filtering (Chemical Mutagenesis)')

        self.assertIsInstance(resolwe, list)
        self.assertEqual(len(resolwe), 1)
        self.assertIsInstance(resolwe[0], dict)
        self.assertEqual(resolwe[0]['name'], 'Variant filtering (Chemical Mutagenesis)')
        self.assertEqual(len(resolwe_mock.api.mock_calls), 1)


class TestResolwePrintUploadProcesses(unittest.TestCase):

    @patch('resdk.resolwe.sys', spec=True)
    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_print_upload_processes(self, resolwe_mock, sys_mock):

        # Check output is correct
        resolwe_mock.processes.return_value = PROCESS_SAMPLE
        sys_mock.stdout.write = MagicMock()
        Resolwe.print_upload_processes(resolwe_mock)
        sys_mock.stdout.write.assert_called_with('Upload NGS reads\n')


class TestResolwePrintProcessInputs(unittest.TestCase):

    @patch('resdk.resolwe.sys', spec=True)
    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_print_process_inpts(self, resolwe_mock, sys_mock):

        # Bad processor name:
        resolwe_mock.processes.return_value = []
        with self.assertRaises(Exception) as exc:
            Resolwe.print_process_inputs(resolwe_mock, 'Bad processor name')
        self.assertRegex(exc.exception.args[0], r"Invalid process name: .*.")  # pylint: disable=deprecated-method

        # Check output is correct
        resolwe_mock.processes.return_value = PROCESS_SAMPLE
        sys_mock.stdout.write = MagicMock()
        Resolwe.print_process_inputs(resolwe_mock, 'Upload NGS reads')
        sys_mock.stdout.write.assert_called_with('src -> basic:file:\n')


class TestResolweCreate(unittest.TestCase):

    @patch('resdk.resolwe.requests')
    @patch('resdk.resolwe.urljoin')
    @patch('resdk.resolwe.json')
    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_create(self, resolwe_mock, json_mock, urljoin_mock, requests_mock):
        resolwe_mock.url = 'http://some/url'
        resolwe_mock.auth = MagicMock()
        json_mock.dumps = MagicMock(return_value="whatever")
        urljoin_mock = MagicMock()
        requests_mock.post = MagicMock(return_value="Something!")

        resolwe = Resolwe.create(resolwe_mock, {"a": "b"})
        self.assertEqual(json_mock.dumps.call_count, 1)
        json_mock.dumps.assert_called_with({"a": "b"})

        # Raise error if data is not dict/str:
        self.assertRaises(ValueError, Resolwe.create, *(resolwe_mock, 666))

        json_mock.dumps.reset_mock()
        resolwe = Resolwe.create(resolwe_mock, "some input")
        self.assertEqual(json_mock.dumps.call_count, 0)
        self.assertEqual(resolwe, "Something!")

        # Raise error on bad name for resource
        self.assertRaises(ValueError, Resolwe.create,
                          *(resolwe_mock, "some input"),
                          **{'resource': "bad_name"})


class TestResolweUpload(unittest.TestCase):

    @patch('resdk.resolwe.os')
    @patch('resdk.resolwe.uuid')
    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_upload(self, resolwe_mock, uuid_mock, os_mock):

        # Bad processor name:
        resolwe_mock.processes.return_value = []
        with self.assertRaises(Exception) as exc:
            Resolwe.upload(resolwe_mock, 'Bad processor name')
        self.assertRegex(exc.exception.args[0], r"Invalid process name: .*.")  # pylint: disable=deprecated-method

        # Bad processor inputs - bad keyword name
        resolwe_mock.processes.side_effect = [PROCESS_SAMPLE, PROCESS_SAMPLE[:1]]
        with self.assertRaises(Exception) as exc:
            Resolwe.upload(resolwe_mock, 'Upload NGS reads', bad_key="Blah.")
        self.assertRegex(  # pylint: disable=deprecated-method
            exc.exception.args[0], r"Field .* not in process .* inputs.")

        # Bad processor inputs - bad keyword value:
        resolwe_mock.processes.side_effect = [PROCESS_SAMPLE, PROCESS_SAMPLE[:1]]
        os_mock.path.isfile.return_value = False
        with self.assertRaises(Exception) as exc:
            Resolwe.upload(resolwe_mock, 'Upload NGS reads', src="/bad/file/name")
        self.assertRegex(exc.exception.args[0], r"File .* not found")  # pylint: disable=deprecated-method

        # Function _upload_file returns None (upload failed):
        resolwe_mock.processes.side_effect = [PROCESS_SAMPLE, PROCESS_SAMPLE[:1]]
        os_mock.path.isfile.return_value = True  # meke look like file is ok
        resolwe_mock._upload_file.return_value = None
        with self.assertRaises(Exception) as exc:
            Resolwe.upload(resolwe_mock, 'Upload NGS reads', src="/file/path")
        self.assertRegex(exc.exception.args[0], r"Upload failed for .*.")  # pylint: disable=deprecated-method

        # All good:
        resolwe_mock.processes.side_effect = [PROCESS_SAMPLE, PROCESS_SAMPLE[:1]]
        os_mock.path.isfile.return_value = True  # pretend it is a valid file name
        uid = '0'*10
        resolwe_mock._upload_file.return_value = uid
        uuid_mock.uuid4.return_value = uid

        Resolwe.upload(resolwe_mock, 'Upload NGS reads', src="/a/b/c/test.txt")

        resolwe_mock._upload_file.assert_called_with("/a/b/c/test.txt")
        data = {u'status': u'uploading',
                u'process': u'import-upload-reads-fastq',
                u'slug': '0000000000',
                u'name': '',
                u'input': {'src': {u'file_temp': '0000000000', u'file': 'test.txt'}}}
        resolwe_mock.create.assert_called_with(data)


class TestResolweUploadFile(unittest.TestCase):

    @patch('resdk.resolwe.requests')
    @patch('resdk.resolwe.sys')
    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_upload_file(self, resolwe_mock, sys_mock, requests_mock):
        # Example file:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files', 'example.fastq')

        resolwe_mock.url = 'http://some/url'

        resolwe_mock.auth = MagicMock()
        # Supress upload progress messages:
        sys_mock.sys.stdout.write = MagicMock()
        sys_mock.sys.stdout.flush = MagicMock()

        # Immitate response form server - always status 200
        requests_response = {'files': [{'temp': 'fake_name'}]}
        requests_mock.post.return_value = MagicMock(status_code=200, **{'json.return_value': requests_response})
        resolwe = Resolwe._upload_file(resolwe_mock, fn)
        self.assertEqual(resolwe, 'fake_name')

        # Immitate response form server - always status 400
        requests_mock.post.return_value = MagicMock(status_code=400)
        resolwe = Resolwe._upload_file(resolwe_mock, fn)
        self.assertIsNone(resolwe)

        # Immitate response form server - one status 400, but other 200
        requests_response = {'files': [{'temp': 'fake_name'}]}
        response_ok = MagicMock(status_code=200, **{'json.return_value': requests_response})
        response_fails = MagicMock(status_code=400)
        requests_mock.post.side_effect = [response_ok, response_fails, response_ok, response_ok]
        resolwe = Resolwe._upload_file(resolwe_mock, fn)
        self.assertEqual(resolwe, 'fake_name')


class TestResolweDownload(unittest.TestCase):

    @patch('resdk.resolwe.urljoin', spec=True)
    @patch('resdk.resolwe.requests', spec=True)
    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_download(self, resolwe_mock, requests_mock, urljoin_mock):

        # Case#1: Field != "output.*"
        with self.assertRaises(ValueError) as exc:
            Resolwe.download(resolwe_mock, [1], 'somthing.wierd')
        msg = "Only process results (output.* fields) can be downloaded."
        self.assertEqual(exc.exception.args[0], msg)

        # Case#2: Invalid object ID:
        with self.assertRaises(ValueError) as exc:
            Resolwe.download(resolwe_mock, ['not_a_number'], 'output.abc')
        self.assertRegex(exc.exception.args[0], "Invalid object id .*")  # pylint: disable=deprecated-method

        # Case#3: not in cache, bad ID
        resolwe_mock.cache = {'data': {}}
        magic_mock1 = MagicMock(**{'get.side_effect': [HttpNotFoundError()]})
        resolwe_mock.api = MagicMock(**{'data.return_value': magic_mock1})
        with self.assertRaises(ValueError) as exc:
            Resolwe.download(resolwe_mock, [123], 'output.abc')
        self.assertRegex(exc.exception.args[0], "Data id .* does not exist.")  # pylint: disable=deprecated-method

        # Case#4: data ID not in cache, field not in annotation
        magic_mock1 = MagicMock(**{'get.return_value': DATA_SAMPLE[0]})
        resolwe_mock.api = MagicMock(**{'data.return_value': magic_mock1})
        with self.assertRaises(ValueError) as exc:
            Resolwe.download(resolwe_mock, [13], 'output.abc')
        msg = "Field .* does not exist for data object .*."
        self.assertRegex(exc.exception.args[0], msg)  # pylint: disable=deprecated-method

        # Case#5: filend type not basic:file:
        with self.assertRaises(ValueError) as exc:
            Resolwe.download(resolwe_mock, [13], 'output.bases')
        self.assertEqual(exc.exception.args[0], "Only basic:file: fields can be downloaded.")

        # Case#6: Requests response with status code 404:
        resolwe_mock.url = 'http://some/url'
        resolwe_mock.auth = 'any_object'
        urljoin_mock.return_value = 'http://another/url'
        magic_mock1 = MagicMock(**{'raise_for_status.side_effect': [requests.exceptions.HTTPError()]})
        magic_mock1.configure_mock(ok=False)
        requests_mock.get.return_value = magic_mock1
        with self.assertRaises(requests.exceptions.HTTPError) as exc:
            Resolwe.download(resolwe_mock, [13], 'output.fastq')

        # "All good" scenario should be tested in end-to-end tests.


class TestResolweResAuth(unittest.TestCase):

    @patch('resdk.resolwe.requests')
    @patch('resdk.resolwe.ResAuth', spec=True)
    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_res_auth(self, resolwe_mock, auth_mock, requests_mock):

        # Wrong URL:
        requests_mock.post = MagicMock(side_effect=[requests.exceptions.ConnectionError()])
        with self.assertRaises(Exception) as exc:
            ResAuth.__init__(auth_mock, email='a', password='p', url='www.abc.com')
        self.assertRegex(exc.exception.args[0], r"Server not accessible on .*.")  # pylint: disable=deprecated-method

        # Wrong credentials:
        magic_mock1 = MagicMock(status_code=400)
        requests_mock.post = MagicMock(return_value=magic_mock1)
        with self.assertRaises(Exception) as exc:
            ResAuth.__init__(auth_mock, email='a', password='p', url='www.abc.com')
        msg = r'Response HTTP status code .* Invalid credentials?'
        self.assertRegex(exc.exception.args[0], msg)  # pylint: disable=deprecated-method

        # NO CSRF token:
        magic_mock1 = MagicMock(status_code=200, cookies={'sessionid': 42})
        requests_mock.post = MagicMock(return_value=magic_mock1)
        with self.assertRaises(Exception) as exc:
            ResAuth.__init__(auth_mock, email='a', password='p', url='www.abc.com')
        msg = 'Missing sessionid or csrftoken. Invalid credentials?'
        self.assertRegex(exc.exception.args[0], msg)  # pylint: disable=deprecated-method

        # "All good" scenario should be tested in end-to-end tests.

if __name__ == '__main__':
    unittest.main()
