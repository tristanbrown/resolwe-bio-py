"""
Unit tests for resdk/resources/process.py file.
"""
# pylint: disable=missing-docstring, protected-access

import unittest

from mock import patch, MagicMock

from resdk.resources.process import Process, get_process_id


class TestBaseCollection(unittest.TestCase):

    @patch('resdk.resources.process.Process', spec=True)
    def test_init(self, process_mock):
        process_mock.configure_mock(endpoint="fake_endpoint")
        Process.__init__(process_mock, id=1, resolwe=MagicMock())

    @patch('resdk.resources.process._print_input_line', spec=True)
    @patch('resdk.resources.process.Process', spec=True)
    def test_print_inputs(self, process_mock, print_input_mock):
        process_mock.configure_mock(input_schema="fake_input_schema")
        Process.print_inputs(process_mock)
        print_input_mock.assert_called_once_with('fake_input_schema', 0)

    def test_get_process_id(self):
        process = Process(id=1, resolwe=MagicMock())
        process.id = 1  # this is overriden when initialized
        self.assertEqual(get_process_id(process), 1)

        self.assertEqual(get_process_id(2), 2)


if __name__ == '__main__':
    unittest.main()
