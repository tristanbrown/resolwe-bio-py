"""
Unit tests for resdk/resolwe.py file.
"""
# pylint: disable=missing-docstring, protected-access

import unittest

import six
import slumber

from mock import patch, MagicMock

from resdk.resolwe import ResolweQuery


class TestResolweQuery(unittest.TestCase):

    @patch('resdk.resolwe.Resolwe')
    @patch('resdk.resources.sample.Sample')
    @patch('resdk.resolwe.ResolweQuery', spec=True)
    def test_init(self, resq_mock, resolwe_mock, resource_mock):
        resource_mock.endpoint = "blah"
        ResolweQuery.__init__(resq_mock, resolwe_mock, resource_mock)

    @patch('resdk.resolwe.ResolweQuery', spec=True)
    def test_get(self, resq_mock):

        # User provides correct ID
        resq_mock.api = MagicMock()
        resq_mock.api.get = MagicMock(return_value=[{'id': 40}])
        resq_mock.resolwe = MagicMock()
        resq_mock.resource = MagicMock(return_value="Some response")

        resq_mock.endpoint = 'anything'
        data = ResolweQuery.get(resq_mock, 40)
        self.assertEqual(data, "Some response")
        resq_mock.resource.assert_called_with(id=40, resolwe=resq_mock.resolwe)

        resq_mock.endpoint = 'presample'
        data = ResolweQuery.get(resq_mock, 40)
        self.assertEqual(data, "Some response")
        resq_mock.resource.assert_called_with(id=40, resolwe=resq_mock.resolwe, presample=True)

        # User provides wrong ID.
        message = r'Id: .* does not exist or you dont have access permission.'
        resq_mock.resource = MagicMock(side_effect=[slumber.exceptions.HttpNotFoundError(message)])
        with six.assertRaisesRegex(self, slumber.exceptions.HttpNotFoundError, message):
            ResolweQuery.get(resq_mock, 12345)

        # User provides correct slug.
        resq_mock.api = MagicMock()
        resq_mock.resolwe = MagicMock()
        resq_mock.resource = MagicMock(return_value="Some response")

        resq_mock.endpoint = 'anything'
        data = ResolweQuery.get(resq_mock, "abc")
        self.assertEqual(data, "Some response")
        resq_mock.resource.assert_called_with(slug='abc', resolwe=resq_mock.resolwe)

        resq_mock.endpoint = 'presample'
        data = ResolweQuery.get(resq_mock, "abc")
        self.assertEqual(data, "Some response")
        resq_mock.resource.assert_called_with(slug='abc',
                                              resolwe=resq_mock.resolwe, presample=True)

        # User provides wrong slug.
        message = r'Slug: .* does not exist or you dont have access permission.'
        resq_mock.resource = MagicMock(side_effect=[IndexError(message)])
        with six.assertRaisesRegex(self, IndexError, message):
            ResolweQuery.get(resq_mock, "some-slug")

    @patch('resdk.resolwe.ResolweQuery', spec=True)
    def test_filter(self, resq_mock):

        resq_mock.api = MagicMock()
        resq_mock.api.get = MagicMock(return_value=[{'id': 42}])
        resq_mock.resolwe = MagicMock()
        resq_mock.resource = MagicMock(return_value=12345)
        resq_mock.endpoint = 'anything_but_presample'

        data = ResolweQuery.filter(resq_mock, slug="some-slug")
        self.assertIsInstance(data, list)
        self.assertEqual(data[0], 12345)

        resq_mock.endpoint = 'presample'

        data = ResolweQuery.filter(resq_mock, slug="some-slug")
        self.assertIsInstance(data, list)
        self.assertEqual(data[0], 12345)

    @patch('resdk.resolwe.ResolweQuery', spec=True)
    def test_search(self, resq_mock):
        with six.assertRaisesRegex(self, NotImplementedError, ""):
            ResolweQuery.search(resq_mock)

if __name__ == '__main__':
    unittest.main()
