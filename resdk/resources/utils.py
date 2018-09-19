"""Resource utility functions."""
from __future__ import absolute_import, division, print_function, unicode_literals


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


def get_collection_id(collection):
    """Return id attribute of the object if it is collection, otherwise return given value."""
    return collection.id if type(collection).__name__ == 'Collection' else collection


def get_data_id(data):
    """Return id attribute of the object if it is data, otherwise return given value."""
    return data.id if type(data).__name__ == 'Data' else data


def get_descriptor_schema_id(dschema):
    """Get descriptor schema id.

    Return id attribute of the object if it is descriptor schema,
    otherwise return given value.

    """
    return dschema.id if type(dschema).__name__ == 'DescriptorSchema' else dschema


def get_process_id(process):
    """Return id attribute of the object if it is process, otherwise return given value."""
    return process.id if type(process).__name__ == 'Process' else process


def get_sample_id(sample):
    """Return id attribute of the object if it is sample, otherwise return given value."""
    return sample.id if type(sample).__name__ == 'Sample' else sample


def get_relation_id(relation):
    """Return id attribute of the object if it is relation, otherwise return given value."""
    return relation.id if type(relation).__name__ == 'Relation' else relation


def is_collection(collection):
    """Return ``True`` if passed object is Collection and ``False`` otherwise."""
    return type(collection).__name__ == 'Collection'


def is_data(data):
    """Return ``True`` if passed object is Data and ``False`` otherwise."""
    return type(data).__name__ == 'Data'


def is_descriptor_schema(data):
    """Return ``True`` if passed object is DescriptorSchema and ``False`` otherwise."""
    return type(data).__name__ == 'DescriptorSchema'


def is_process(process):
    """Return ``True`` if passed object is Process and ``False`` otherwise."""
    return type(process).__name__ == 'Process'


def is_sample(sample):
    """Return ``True`` if passed object is Sample and ``False`` otherwise."""
    return type(sample).__name__ == 'Sample'


def is_relation(relation):
    """Return ``True`` if passed object is Relation and ``False`` otherwise."""
    return type(relation).__name__ == 'Relation'


def is_user(user):
    """Return ``True`` if passed object is User and ``False`` otherwise."""
    return type(user).__name__ == 'User'


def is_group(group):
    """Return ``True`` if passed object is Group and ``False`` otherwise."""
    return type(group).__name__ == 'Group'


def get_samples(resource):
    """Get the list of samples from given resources.

    Get the list of samples with:
    * use recursion if given resource is a list
    * return the resource if it is already the sample
    * call ResolweQuery object named `samples` (if exists) and return
      the result
    """
    error_msg = ("Resource should be sample, have `samples` query, be list of multiple "
                 "resources or be data object with not empty `sample` property.")
    if isinstance(resource, list):
        samples = []
        for res in resource:
            samples.extend(get_samples(res))
        return samples

    elif is_data(resource):
        if not resource.sample:
            raise TypeError(error_msg)

        return [resource.sample]

    elif is_sample(resource):
        return [resource]

    elif hasattr(resource, 'samples'):
        return resource.samples

    else:
        raise TypeError(error_msg)


def get_resource_collection(resource, fail_silently=True):
    """Get id of the collection to which resource belongs.

    If resource does not belong to any collection or collection cannot
    be determined uniquely, ``None`` is returned of ``LookupError`` is
    raised (if ``fail_silently`` is set to ``True``).
    """
    if is_collection(resource):
        return resource.id

    elif hasattr(resource, 'collection'):
        return resource.collection.id

    elif hasattr(resource, 'collections'):
        collections = resource.collections
        if len(collections) == 1:
            return collections[0].id

    if fail_silently:
        return None

    raise LookupError('Collection id cannot be determined uniquely.')


def get_resolwe(*resources):
    """Return resolwe object used in given resources.

    Raise an error if there is more than one.
    """
    resolwes = {res_obj.resolwe for res_obj in resources}
    if len(resolwes) != 1:
        raise TypeError('All input objects must be from the same `Resolwe` connection.')

    return list(resolwes)[0]


def is_background(sample):
    """Return ``True`` if given sample is background and ``False`` otherwise."""
    background_relations = sample.resolwe.relation.filter(
        type='compare',
        label='background',
        entity=sample.id,
        position='background'
    )
    return len(background_relations) > 0
