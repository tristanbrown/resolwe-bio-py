"""
Unit tests for resdk/resolwe.py file.
"""
# pylint: disable=missing-docstring, protected-access

import unittest

import six
import slumber
from mock import MagicMock, call, patch

from resdk.resources.base import BaseResolweResource, BaseResource

# This is normally set in subclass
BaseResolweResource.endpoint = 'endpoint'
BaseResource.endpoint = 'endpoint'


class TestBaseResolweResource(unittest.TestCase):

    @patch('resdk.resolwe.Resolwe')
    def setUp(self, resolwe_mock):  # pylint: disable=arguments-differ
        self.resolwe_mock = resolwe_mock

    def test_field_constraints(self):
        base_resource = BaseResolweResource(resolwe=self.resolwe_mock)

        base_resource.WRITABLE_FIELDS = ('writable_scalar', )
        base_resource.READ_ONLY_FIELDS = ('read_only_scalar', )
        base_resource._original_values = {'writable_scalar': None, 'read_only_scalar': None}

        # Setting to same value should be fine.
        base_resource.writable_scalar = None
        base_resource.read_only_scalar = None

        message = 'Can not change read only field read_only_scalar'
        with six.assertRaisesRegex(self, ValueError, message):
            base_resource.read_only_scalar = 42

        base_resource.writable_scalar = '42'
        self.assertEqual(base_resource.writable_scalar, '42')

    def test_fields(self):
        base_resource = BaseResolweResource(resolwe=self.resolwe_mock)
        base_resource.WRITABLE_FIELDS = ('writable', )
        base_resource.UPDATE_PROTECTED_FIELDS = ('update_protected', )
        base_resource.READ_ONLY_FIELDS = ('read_only', )
        self.assertEqual(base_resource.fields(), ('writable', 'update_protected', 'read_only'))

    def test_dehydrate_resources(self):
        obj = BaseResource(resolwe=self.resolwe_mock, id=1)

        self.assertEqual(obj._dehydrate_resources(obj), 1)
        self.assertEqual(obj._dehydrate_resources([obj]), [1])
        self.assertEqual(obj._dehydrate_resources({'key': obj}), {'key': 1})
        self.assertEqual(obj._dehydrate_resources({'key': [obj]}), {'key': [1]})

    def test_update_fileds(self):
        resource = BaseResource(resolwe=self.resolwe_mock)
        resource.WRITABLE_FIELDS = ('first_field',)
        resource.first_field = None

        payload = {'first_field': 42}

        resource._update_fields(payload)

        self.assertEqual(resource.first_field, 42)

    def test_eq(self):
        obj_1 = BaseResource(resolwe=self.resolwe_mock, id=1)
        obj_2 = BaseResource(resolwe=self.resolwe_mock, id=1)
        obj_3 = BaseResource(resolwe=self.resolwe_mock, id=2)
        obj_4 = BaseResolweResource(resolwe=self.resolwe_mock, id=1)

        self.assertEqual(obj_1 == obj_2, True)
        self.assertEqual(obj_1 == obj_3, False)
        self.assertEqual(obj_1 == obj_4, False)


class TestBaseMethods(unittest.TestCase):

    @patch('resdk.resources.base.setattr')
    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_update_fields(self, base_mock, setattr_mock):
        fields = {'id': 1, 'slug': 'testobj'}
        base_mock.fields.return_value = ('id', 'slug')
        BaseResolweResource._update_fields(base_mock, fields)
        setattr_mock.assert_has_calls(
            [call(base_mock, 'id', 1), call(base_mock, 'slug', 'testobj')], any_order=True
        )

    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_save_post(self, base_mock):
        base_mock.configure_mock(id=None, slug='test')
        base_mock.WRITABLE_FIELDS = ('slug', )
        base_mock.api = MagicMock(**{'post.return_value': {'id': 1, 'slug': 'test'}})
        BaseResolweResource.save(base_mock)
        self.assertEqual(base_mock._update_fields.call_count, 1)

    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_save_post_read_only(self, base_mock):
        base_mock.configure_mock(id=None, slug='test', read_only_dict=None, _original_values={})
        base_mock.READ_ONLY_FIELDS = ('id', 'read_only_dict')
        base_mock.UPDATE_PROTECTED_FIELDS = ()
        base_mock.WRITABLE_FIELDS = ('slug', )
        base_mock.fields.return_value = ('id', 'slug', 'read_only_dict')

        base_mock.read_only_dict = {'change': 'change-not-allowed'}

        message = 'Not allowed to change read only fields read_only_dict'
        with six.assertRaisesRegex(self, ValueError, message):
            BaseResolweResource.save(base_mock)

    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_save_post_update_protected(self, base_mock):
        base_mock.configure_mock(id=None, slug='test', update_protected_dict=None,
                                 _original_values={})
        base_mock.READ_ONLY_FIELDS = ('id', )
        base_mock.UPDATE_PROTECTED_FIELDS = ('update_protected_dict', )
        base_mock.WRITABLE_FIELDS = ('slug', )
        base_mock.fields.return_value = ('id', 'slug', 'update_protected_dict')

        base_mock.update_protected_dict = {'create': 'create-allowed'}
        base_mock.api = MagicMock(**{'post.return_value': {
            'id': 1, 'slug': 'test', 'update_protected_dict': {'create': 'create-allowed'}}})

        BaseResolweResource.save(base_mock)
        self.assertEqual(base_mock.update_protected_dict, {'create': 'create-allowed'})

    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_save_post_client_error(self, base_mock):
        base_mock.configure_mock(id=None, slug='test')
        base_mock.api = MagicMock(**{'post.side_effect': slumber.exceptions.HttpClientError(
            message='', content='', response='')})

        with self.assertRaises(slumber.exceptions.HttpClientError):
            BaseResolweResource.save(base_mock)
        self.assertEqual(base_mock._update_fields.call_count, 0)

    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_save_patch(self, base_mock):
        base_mock.configure_mock(id=1, slug='test', _original_values={'slug': 'test-old'})
        base_mock.WRITABLE_FIELDS = ('slug', )

        base_mock.api = MagicMock(**{'patch.return_value': {'id': 1, 'slug': 'test'}})
        BaseResolweResource.save(base_mock)
        self.assertEqual(base_mock._update_fields.call_count, 1)

    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_save_patch_read_only(self, base_mock):
        base_mock.READ_ONLY_FIELDS = ('id', 'read_only_dict')
        base_mock.UPDATE_PROTECTED_FIELDS = ()
        base_mock.WRITABLE_FIELDS = ('slug', )
        base_mock.fields.return_value = ('id', 'slug', 'read_only_dict')
        read_only_dict = {}
        BaseResolweResource._update_fields(
            base_mock,
            {
                'id': 1,
                'slug': 'test',
                'read_only_dict': read_only_dict
            }
        )
        base_mock.read_only_dict['change'] = 'change-not-allowed'

        message = 'Not allowed to change read only fields read_only_dict'
        with six.assertRaisesRegex(self, ValueError, message):
            BaseResolweResource.save(base_mock)

    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_save_patch_update_protect(self, base_mock):
        base_mock.READ_ONLY_FIELDS = ('id', )
        base_mock.UPDATE_PROTECTED_FIELDS = ('update_protected_dict', )
        base_mock.WRITABLE_FIELDS = ('slug', )
        base_mock.fields.return_value = ('id', 'slug', 'update_protected_dict')
        update_protected_dict = {}
        BaseResolweResource._update_fields(
            base_mock,
            {
                'id': 1,
                'slug': 'test',
                'update_protected_dict': update_protected_dict
            }
        )
        base_mock.update_protected_dict['change'] = 'change-not-allowed'

        message = 'Not allowed to change read only fields update_protected_dict'
        with six.assertRaisesRegex(self, ValueError, message):
            BaseResolweResource.save(base_mock)

        base_mock.UPDATE_PROTECTED_FIELDS = ('id', 'update_protected_dict')

    @patch('resdk.resources.base.BaseResolweResource', spec=True)
    def test_repr(self, base_mock):
        base_mock.configure_mock(id=1, slug='a', name='b')
        out = BaseResolweResource.__repr__(base_mock)
        self.assertEqual(out, 'BaseResolweResource <id: 1, slug: \'a\', name: \'b\'>')


if __name__ == '__main__':
    unittest.main()
