"""Resolwe"""
from __future__ import absolute_import, division, print_function

import json
import os
import re
import sys
import uuid
import ntpath

import requests
import slumber

from .data import Data
from .collection import Collection
from .utils import find_field, iterate_schema

from requests.exceptions import ConnectionError

if sys.version_info < (3, ):
    import urlparse
else:
    from urllib import parse as urlparse

CHUNK_SIZE = 90000000
DEFAULT_EMAIL = 'anonymous@genialis.com'
DEFAULT_PASSWD = 'anonymous'
DEFAULT_URL = 'https://dictyexpress.research.bcm.edu'


class Resolwe(object):

    """Python API for Resolwe Bioinformatics."""

    def __init__(self, email=DEFAULT_EMAIL, password=DEFAULT_PASSWD, url=DEFAULT_URL):
        """
        Connect to Resolwe on desired url and provide credentials.
        """
        self.url = url
        self.auth = ResAuth(email, password, url)
        self.api = slumber.API(urlparse.urljoin(url, '/api/'), self.auth, append_slash=False)

        # data = dict of (data_id - Data object) pairs
        # collections = dict of (collection_id - Collection object) pairs
        # collections_data - dict of (collection_id - Data objects list) pairs,
        self.cache = {'data': {}, 'collections': None, 'collections_data': {}}
        # TODO: what if there are updates on server? How to know when to update cache?

    def collections(self):
        """Return a list :obj:`Collection` collections.

        :rtype: list of :obj:`Collection` collections

        """
        if not ('collections' in self.cache and self.cache['collections']):
            self.cache['collections'] = {c['id']: Collection(c, self) for c in
                                         self.api.collection.get()}
        return self.cache['collections']

        # TODO what if person does not have access to some data objects?
        # Should output be somehow different?

    def collection_data(self, collection):
        """Return a list of Data objects for a given collection.

        :param collection: ObjectId or slug of a collection
        :type collection: string
        :rtype: list of Data objects

        """
        #
        cache_collections_data = self.cache['collections_data']
        cache_data = self.cache['data']

        # Ensure that collection is not a slug, but ID number.
        if not re.match('^[0-9]+$', str(collection)):
            collections = self.api.collection.get(**{'slug': str(collection)})
            if len(collections) != 1:
                raise ValueError('Parameter {} is not a valid collection slug.'.format(collection))

            collection = collections[0]['id']

        if collection not in cache_collections_data:
            try:
                data_id_list = self.api.collection(collection).get()['data']
            except slumber.exceptions.HttpNotFoundError:
                raise ValueError("Collections id {} does not exist.".format(collection))
            if len(data_id_list) == 0:
                return []

            cache_collections_data[collection] = []

            data = [self.api.data(id_).get() for id_ in data_id_list]
            for d in data:
                # First update all retrieved data in cache_data
                data_id = d['id']
                if data_id in cache_data:
                    cache_data[data_id].update(d)
                else:
                    cache_data[data_id] = Data(d, self)

                cache_collections_data[collection].append(cache_data[data_id])

            # Hydrate reference fields
            # TODO: This is inconsistent - we only do it for data objects in cache.
            for d in cache_collections_data[collection]:
                while True:
                    ref_annotation = {}
                    remove_annotation = []
                    for path, ann in d.annotation.items():
                        if ann['type'].startswith('data:'):
                            # Referenced data object found
                            # Copy annotation
                            if ann['value'] in self.cache['objects']:
                                annotation = self.cache['objects'][ann['value']].annotation
                                ref_annotation.update({path + '.' + k: v for k, v in
                                                      annotation.items()})

                            remove_annotation.append(path)
                    if ref_annotation:
                        d.annotation.update(ref_annotation)
                        for path in remove_annotation:
                            del d.annotation[path]
                    else:
                        break

        return cache_collections_data[collection]

    def data(self, **query):
        """
        Query for Data object annotation.

        Querries can be made with the following keywords (and operators)

            * Fields (and possible operators):
                * slug (=)
                    * Example: resolwe.data(slug="some_slug")
                * contributor (=)
                    * Example: resolwe.data(contributor="some_slug")
                * status (=)
                    * Example: resolwe.data(contributor="1", status="ER")
                * name (=)
                * created (=)
                * modified (=)
                * input (=)
                * descriptor (=)
                * started (=)
                * finished (=)
                * output (=)
                * process (=)
                * type (=)
                * collection (=)

        Examples:

        * resolwe.data(slug="some_slug")
        * resolwe.data(contributor="1", status="ER")

        Note: filtering will probably change/upgrade, it is defined in: resolwe/flow/filters.py
        """
        objects = self.cache['data']
        data = self.api.data.get(**query)
        data_objects = []

        for d in data:
            _id = d['id']
            if _id in objects:
                objects[_id].update(d)
            else:
                objects[_id] = Data(d, self)

            data_objects.append(objects[_id])

        # Hydrate reference fields
        count = 0
        for d in data_objects:
            count += 1
            while True:
                ref_annotation = {}
                remove_annotation = []
                for path, ann in d.annotation.items():
                    if ann['type'].startswith('data:'):
                        # Referenced data object found
                        # Copy annotation
                        _id = ann['value']
                        if _id not in objects:
                            try:
                                d_tmp = self.api.data(_id).get()
                            except slumber.exceptions.HttpClientError as ex:
                                if ex.response.status_code == 404:
                                    continue
                                else:
                                    raise ex

                            objects[_id] = Data(d_tmp, self)

                        annotation = objects[_id].annotation
                        ref_annotation.update({path + '.' + k: v for k, v in annotation.items()})
                        remove_annotation.append(path)
                if ref_annotation:
                    d.annotation.update(ref_annotation)
                    for path in remove_annotation:
                        del d.annotation[path]
                else:
                    break

        return data_objects

    def processes(self, process_name=None):
        """Return a list of Processor objects.

        :param process_name: Name of the process
        :type process_name: string
        :rtype: list of Process objects

        """
        # TODO: Make a better representation? If this is run from command line
        # it outputs thousands of lines... Not really helpful.
        if process_name:
            return [p for p in self.api.process.get() if process_name in p['name']]
        else:
            return self.api.process.get()

    def print_upload_processes(self):
        """Print all upload process names."""
        for p in self.processes():
            if 'upload' in p['category']:
                sys.stdout.write(p['name'] + '\n')

    def print_process_inputs(self, process_name):
        """Print process input fields and types.

        :param process_name: Process object name
        :type process_name: string

        """
        p = self.processes(process_name=process_name)

        if len(p) == 1:
            p = p[0]
        elif len(p) > 1:
            # Multiple processors with same slug, but different versions:
            versions = ([int(x['version']) for x in p])
            # Get index of the latest processor version:
            top_index = sorted(enumerate(versions), key=lambda x: x[1])[-1][0]
            p = p[top_index]
        else:
            raise ValueError('Invalid process name: {}.'.format(process_name))

        for field_schema, _, _ in iterate_schema({}, p['input_schema'], 'input'):
            name = field_schema['name']
            typ = field_schema['type']
            sys.stdout.write("{} -> {}".format(name, typ))

    def create(self, data, resource='data'):
        """Create an object of resource:

        * data
        * collection
        * process
        * trigger
        * template

        :param data: Object values
        :type data: dict
        :param resource: Resource name
        :type resource: string

        """
        if isinstance(data, dict):
            data = json.dumps(data)

        if not isinstance(data, str):
            raise ValueError('Data must be dict, str or unicode.')

        resource = resource.lower()
        if resource not in ('data', 'collection', 'process', 'trigger', 'template'):
            raise ValueError('Resource must be data, collection, process, trigger or template.')

        url = urlparse.urljoin(self.url, '/api/{}'.format(resource))
        return requests.post(url,
                             data=data,
                             auth=self.auth,
                             headers={
                                 'cache-control': 'no-cache',
                                 'content-type': 'application/json',
                                 'accept': 'application/json, text/plain, */*',
                                 'referer': self.url,
                             })

    def upload(self, process_name, name='', descriptor=None, descriptor_schema=None,
               collections=[], **fields):

        """Upload files and data objects.

        :param collections: Integer id of Resolwe collection
        :type collections: List of int
        :param process_name: Processor object name
        :type process_name: string
        :param fields: Processor field-value pairs
        :type fields: args
        :rtype: HTTP Response object

        """
        # This is temporary solution: map process name to it's ID:
        proc_name_to_slug = dict([(x['name'], x['slug']) for x in self.processes()])

        p = self.processes(process_name=process_name)

        if len(p) == 1:
            p = p[0]
        elif len(p) > 1:
            # Multiple processors with same slug, but different versions:
            versions = ([int(x['version']) for x in p])
            # Get index of the latest processor version:
            top_index = sorted(enumerate(versions), key=lambda x: x[1])[-1][0]
            p = p[top_index]
        else:
            raise ValueError('Invalid process name: {}.'.format(process_name))

        inputs = {}

        for field_name, field_val in fields.items():
            input_fields = dict([(e['name'], e['type']) for e in p['input_schema']])
            if field_name not in input_fields.keys():
                raise ValueError("Field {} not in process {} inputs.".format(field_name, p['name']))

            if input_fields[field_name].startswith('basic:file:'):
                if not os.path.isfile(field_val):
                    raise ValueError("File {} not found.".format(field_val))

                file_temp = self._upload_file(field_val)

                if not file_temp:
                    raise Exception("Upload failed for {}.".format(field_val))

                file_name = ntpath.basename(field_val)
                inputs[field_name] = {
                    'file': file_name,
                    'file_temp': file_temp
                }
            else:
                inputs[field_name] = field_val

        d = {
            'status': 'uploading',
            'process': proc_name_to_slug[process_name],
            'input': inputs,
            'slug': str(uuid.uuid4()),
            'name': name,
        }

        if descriptor:
            d['descriptor'] = descriptor

        if descriptor_schema:
            d['descriptor_schema'] = descriptor_schema

        if len(collections) > 0:
            d['collections'] = collections

        return self.create(d)

    def _upload_file(self, fn):
        """Upload a single file on the platform.

        File is uploaded in chunks of 1,024 bytes.

        :param fn: File path
        :type fn: string

        """
        response = None
        chunk_number = 0
        session_id = str(uuid.uuid4())
        file_size = os.path.getsize(fn)
        base_name = os.path.basename(fn)

        with open(fn, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break

                for i in range(5):
                    if i > 0 and response is not None:
                        sys.stdout.write("Chunk upload failed (error {}): repeating for chunk \
                                         number {}".format(response.status_code, chunk_number))

                    response = requests.post(urlparse.urljoin(self.url, 'upload/'),
                                             auth=self.auth,

                                             # request are smart and make
                                             # 'CONTENT_TYPE': 'multipart/form-data;''
                                             files={'file': (base_name, chunk)},

                                             # stuff in data will be in response.POST on server
                                             data={
                                                 '_chunkSize': CHUNK_SIZE,
                                                 '_totalSize': file_size,
                                                 '_chunkNumber': chunk_number,
                                                 '_currentChunkSize': len(chunk),
                                             },
                                             headers={
                                                 'Session-Id': session_id
                                             })
                    if response.status_code in [200, 201]:
                        break
                else:
                    # Upload of a chunk failed (5 retries)
                    return None

                progress = 100. * (chunk_number * CHUNK_SIZE + len(chunk)) / file_size
                sys.stdout.write("\n{:.0f} % Uploaded {}".format(progress, fn))
                sys.stdout.flush()
                chunk_number += 1

        sys.stdout.write("\n")
        return response.json()['files'][0]['temp']

    def download(self, data_objects, field):
        """Download files of data objects.

        :param data_objects: Data object ids
        :type data_objects: list of integers
        :param field: Download field name
        :type field: string
        :rtype: generator of requests.Response objects

        """
        if not field.startswith('output'):
            raise ValueError("Only process results (output.* fields) can be downloaded.")

        for o in data_objects:
            if re.match('^\d+$', str(o)) is None:
                raise ValueError("Invalid object id {}.".format(o))

            if o not in self.cache['data']:
                try:
                    self.cache['data'][o] = Data(self.api.data(o).get(), self)
                except slumber.exceptions.HttpNotFoundError:
                    raise ValueError("Data id {} does not exist.".format(o))

            if field not in self.cache['data'][o].annotation:
                raise ValueError("Field {} does not exist for data object {}.".format(field, o))

            ann = self.cache['data'][o].annotation[field]
            if ann['type'] != 'basic:file:':
                raise ValueError("Only basic:file: fields can be downloaded.")

        for o in data_objects:
            ann = self.cache['data'][o].annotation[field]
            url = urlparse.urljoin(self.url, 'data/{}/{}'.format(o, ann['value']['file']))
            response = requests.get(url, stream=True, auth=self.auth)
            if not response.ok:
                response.raise_for_status()
            else:
                return response


class ResAuth(requests.auth.AuthBase):

    """
    Attach HTTP Resolwe Authentication to Request object.
    """

    def __init__(self, email=DEFAULT_EMAIL, password=DEFAULT_PASSWD, url=DEFAULT_URL):
        payload = {'username': email, 'password': password}

        try:
            response = requests.post(urlparse.urljoin(url, '/rest-auth/login/'), data=payload)
        except ConnectionError:
            raise ValueError('Server not accessible on {}. Wrong url?'.format(url))

        sc = response.status_code
        if sc in [400, 403]:
            raise ValueError('Response HTTP status code {}. Invalid credentials?'.format(sc))

        if not ('sessionid' in response.cookies and 'csrftoken' in response.cookies):
            raise Exception('Missing sessionid or csrftoken. Invalid credentials?')

        self.sessionid = response.cookies['sessionid']
        self.csrftoken = response.cookies['csrftoken']
        # self.subscribe_id = str(uuid.uuid4())

    def __call__(self, request):
        # modify and return the request
        request.headers['Cookie'] = 'csrftoken={}; sessionid={}'.format(self.csrftoken,
                                                                        self.sessionid)
        request.headers['X-CSRFToken'] = self.csrftoken

        # Not needed until we support HTTP Push with the API
        # if r.path_url != '/upload/':
        #     r.headers['X-SubscribeID'] = self.subscribe_id
        return request
