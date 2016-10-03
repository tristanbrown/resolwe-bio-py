"""Constants and abstract classes."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import operator

import six
import slumber


class BaseResource(object):
    """Abstract resource.

    One and only one of the identifiers (slug, id or model_data)
    should be given.

    :param slug: Resource slug
    :type slug: str
    :param id: Resource ID
    :type id: int
    :param model_data: Resource model data
    :type model_data: dict
    :param resolwe: Resolwe instance
    :type resolwe: Resolwe object

    """

    endpoint = None

    WRITABLE_FIELDS = ('slug', 'name', 'permissions')
    UPDATE_PROTECTED_FIELDS = ('contributor', )
    READ_ONLY_FIELDS = ('id', 'created', 'modified')

    def __init__(self, slug=None, id=None,  # pylint: disable=redefined-builtin
                 model_data=None, resolwe=None):
        """Verify that only a single attribute of slug, id or model_data given."""
        if len([attr for attr in (slug, id, model_data) if attr is not None]) > 1:
            raise ValueError("Only one of slug, id or model_data allowed")

        if id:
            if not isinstance(id, int):
                raise ValueError("id should be an integer.")
        elif slug:
            if not isinstance(slug, six.string_types):
                raise ValueError("slug should be a string.")
        elif model_data:
            if not isinstance(model_data, dict):
                raise ValueError("model_data should be a dict.")

        self._original_values = {}

        for field_name in self.fields():
            setattr(self, field_name, None)

        #: a descriptive name of the resource
        self.name = None
        #: unique identifier
        self.id = id  # pylint: disable=invalid-name
        #: human-readable unique identifier
        self.slug = slug
        #: user id of the contributor
        self.contributor = None
        #: date of creation
        self.created = None
        #: date of latest modification
        self.modified = None
        #: permissions - (view/download/add/edit/share/owner for user/group/public)
        self.permissions = None

        self.api = operator.attrgetter(self.endpoint)(resolwe.api)
        self.resolwe = resolwe

        if id:
            try:
                self._update_fields(self.api(id).get())
            except slumber.exceptions.HttpNotFoundError:
                raise ValueError("ID '{}' does not exist or you do not "
                                 "have access permission.".format(id))
        elif slug:
            resources = self.api.get(slug=slug)  # pylint: disable=no-member

            if len(resources) > 1:
                # Return the latest version
                resources.sort(key=lambda resource: resource['version'], reverse=True)
            elif len(resources) < 1:
                raise ValueError("Slug '{}' does not exist or you do not "
                                 "have access permission.".format(slug))

            self._update_fields(resources[0])
        elif model_data:
            self._update_fields(model_data)

        self.logger = logging.getLogger(__name__)

    def fields(self):
        """Resource fields."""
        return self.WRITABLE_FIELDS + self.UPDATE_PROTECTED_FIELDS + self.READ_ONLY_FIELDS

    def _update_fields(self, payload):
        """Update resource fields.

        :param payload: Resource fields
        :type payload: dict

        """
        self._original_values = payload
        for field_name in self.fields():
            setattr(self, field_name, payload.get(field_name, None))

    def update(self):
        """Update resource fields from the server."""
        response = self.api(self.id).get()
        self._update_fields(response)

    def save(self):
        """Save resource to the server."""
        if self.id:  # update resource
            payload = {}
            for field_name in self.WRITABLE_FIELDS:
                # find changes
                if getattr(self, field_name) != self._original_values.get(field_name):
                    payload[field_name] = getattr(self, field_name)

            if payload:
                response = self.api(self.id).patch(payload)
                self._update_fields(response)

        else:  # create resource
            try:
                field_names = self.WRITABLE_FIELDS + self.UPDATE_PROTECTED_FIELDS
                payload = {field_name: getattr(self, field_name) for field_name in field_names
                           if getattr(self, field_name) is not None}

                response = self.api.post(payload)
                self._update_fields(response)
            except slumber.exceptions.HttpClientError as ex:
                # pylint: disable=no-member
                raise slumber.exceptions.HttpClientError('{}\n\n{}'.format(ex.message, ex.content),
                                                         response=ex.response,
                                                         content=ex.content)

    def delete(self):
        """Delete the resource object from the server."""
        self.api(self.id).delete()

    def __repr__(self):
        """Format resource name."""
        return "{} <id: {}, slug: '{}', name: '{}'>".format(self.__class__.__name__,
                                                            self.id, self.slug, self.name)
