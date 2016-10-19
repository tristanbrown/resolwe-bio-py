"""Resource utility functions."""
from __future__ import absolute_import, division, print_function, unicode_literals

from .base import BaseResource


def iterate_fields(fields, schema):
    """Recursively iterate over all DictField sub-fields.

    :param fields: Field instance (e.g. input)
    :type fields: dict
    :param schema: Schema instance (e.g. input_schema)
    :type schema: dict

    """
    schema_dict = {val['name']: val for val in schema}
    for field_id, properties in fields.items():
        if 'group' in schema_dict[field_id]:
            for _field_sch, _fields in iterate_fields(properties, schema_dict[field_id]['group']):
                yield (_field_sch, _fields)
        else:
            yield (schema_dict[field_id], fields)


def find_field(schema, field_name):
    """Find field in schema by field name.

    :param schema: Schema instance (e.g. input_schema)
    :type schema: dict
    :param field_name: Field name
    :type field_name: string

    """
    for field in schema:
        if field['name'] == field_name:
            return field


def iterate_schema(fields, schema, path=None):
    """Recursively iterate over all schema sub-fields.

    :param fields: Field instance (e.g. input)
    :type fields: dict
    :param schema: Schema instance (e.g. input_schema)
    :type schema: dict
    :path schema: Field path
    :path schema: string

    """
    for field_schema in schema:
        name = field_schema['name']
        if 'group' in field_schema:
            for rvals in iterate_schema(fields[name] if name in fields else {},
                                        field_schema['group'],
                                        None if path is None else '{}.{}'.format(path, name)):
                yield rvals
        else:
            if path is None:
                yield (field_schema, fields)
            else:
                yield (field_schema, fields, '{}.{}'.format(path, name))


def fill_spaces(word, desired_length):
    """Fill spaces at the end until word reaches desired length."""
    return str(word) + ' ' * (desired_length - len(word))


def _print_input_line(element_list, level):
    """Pretty print of input_schema."""
    spacing = 2

    for element in element_list:
        if "group" in element:
            print("{}- {} - {}".format('    ' * level, element['name'], element['label']))
            _print_input_line(element['group'], level + 1)
        else:
            max_name_len = max([len(elm['name']) for elm in element_list])
            max_type_len = max([len(elm['type']) or 0 for elm in [e for e in element_list if
                                                                  'group' not in e]])
            print("{}- {} {} - {}".format(
                '    ' * level,
                fill_spaces(element['name'], max_name_len + spacing),
                fill_spaces("[" + element['type'] + "]", max_type_len + spacing),
                element['label']))


def endswith_colon(schema, field):
    """Ensure the field ends with colon.

    :param schema: Register process from source YAML file
    :type schema: dict
    :param field: field name
    :type field: str

    """
    if field in schema and not schema[field].endswith(':'):
        schema[field] += ':'


def get_resource_id(resource):
    """Return id attribute of the object if it is resorce, othervise return given value."""
    return resource.id if isinstance(resource, BaseResource) else resource


class resource_list(list):  # pylint: disable=invalid-name
    """Subclass of ``list`` used for resdk resources.

    This list is aware of resource objects it holds and knows how to compare
    them with a list of just object ids.

    """

    def __ne__(self, other):
        """Chech if given two objects are NOT equal."""
        if other is None:
            other = []

        if len(self) != len(other):
            return True

        for obj1, obj2 in zip(self, other):
            if get_resource_id(obj1) != get_resource_id(obj2):
                return True

        return False

    def __eq__(self, other):
        """Chech if given two objects are equal."""
        return not self.__ne__(other)
