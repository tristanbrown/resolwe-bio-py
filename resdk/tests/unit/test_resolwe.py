"""
Unit tests for resdk/resolwe.py file.
"""
# pylint: disable=missing-docstring, protected-access

import os
import unittest
import six

from mock import patch, MagicMock
import requests

from resdk.resolwe import Resolwe, ResAuth

if six.PY2:
    # pylint: disable=deprecated-method
    unittest.TestCase.assertRegex = unittest.TestCase.assertRegexpMatches


class TestResolweUploadFile(unittest.TestCase):

    @patch('resdk.resolwe.requests')
    @patch('resdk.resolwe.Resolwe', spec=True)
    def test_upload_file(self, resolwe_mock, requests_mock):
        # Example file:
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'files', 'example.fastq')

        resolwe_mock.url = 'http://some/url'

        resolwe_mock.auth = MagicMock()
        resolwe_mock.logger = MagicMock()

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
