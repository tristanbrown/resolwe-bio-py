"""Permissions manager class."""
from __future__ import absolute_import, division, print_function, unicode_literals

import copy
from collections import defaultdict

from .utils import is_group, is_user


class PermissionsManager(object):
    """Helper class to manage permissions of the :class:`BaseResource`."""

    #: (lazy loaded) list of permissons on current object
    _permissions = None

    def __init__(self, all_permissions, api_root, resolwe):
        """Initialize attributes."""
        self.all_permissions = all_permissions
        self.permissions_api = api_root.permissions
        self.resolwe = resolwe

    def _fetch_users(self, users):
        if not isinstance(users, list):
            users = [users]

        return [self.resolwe.user.get(user) if not is_user(user) else user for user in users]

    def _fetch_group(self, groups):
        if not isinstance(groups, list):
            groups = [groups]

        return [
            self.resolwe.group.get(group) if not is_group(group) else group for group in groups
        ]

    def _validate_perms(self, perms):
        """Check that given list of permissions is valid for current object type."""
        for perm in perms:
            if perm not in self.all_permissions:
                valid_perms = ', '.join(["'{}'".format(p) for p in self.all_permissions])
                raise ValueError(
                    "Invalid permission '{}' for type '{}'. Valid permissions are: {}".format(
                        perm, self.__class__.__name__, valid_perms
                    )
                )

    def _set_permissions(self, action, perms, who_type, who=None):
        """Generate permissions payload and post it to the API."""
        payload = {
            'users': defaultdict(lambda: defaultdict(list)),
            'groups': defaultdict(lambda: defaultdict(list)),
            'public': defaultdict(list)
        }

        if not isinstance(perms, list):
            perms = [perms]

        self._validate_perms(perms)

        if who_type in ['users', 'groups']:
            for single in who:
                payload[who_type][action][single.id] = copy.copy(perms)

        elif who_type == 'public':
            payload[who_type][action] = copy.copy(perms)

        else:
            raise KeyError("`who_type` must be 'users', 'groups' or 'public'.")

        self._permissions = self.permissions_api.post(payload)

    def clear_cache(self):
        """Clear cache."""
        self._permissions = None

    def fetch(self):
        """Fetch permissions from server."""
        if self._permissions is None:
            self._permissions = self.permissions_api.get()

    def add_user(self, user, perms):
        """Add ``perms`` permissions to ``user``.

        ``user`` can be single ``User`` object, username, user id, or
        list of previous items.

        Example:

        If you want to add ``view`` permission on a ``My Collection``
        to the user ``john``, run following code:

        .. code-block:: python

            collection = res.collection.get(name='My Collection')
            collection.permissions.add_user('john', 'view')

        For advanced use-cases we also support more complex syntax
        like:

        .. code-block:: python

            john = res.user.get('john')
            mary = res.user.get('mary')
            collection = res.collection.get(name='My Collection')
            collection.permissions.add_user([john, mary], ['view', 'edit'])

        """
        self._set_permissions('add', perms, 'users', self._fetch_users(user))

    def remove_user(self, user, perms):
        """Remove ``perms`` permissions from ``user``.

        ``user`` can be single ``User`` object, username user id, or
        list of of previous items.

        Example:

        If you want to remove ``view`` permission on a
        ``My Collection`` from the user ``john``, run following code:

        .. code-block:: python

            collection = res.collection.get(name='My Collection')
            collection.permissions.remove_user('john', 'view')

        For advanced use-cases we also support more complex syntax
        like:

        .. code-block:: python

            john = res.user.get('john')
            mary = res.user.get('mary')
            collection = res.collection.get(name='My Collection')
            collection.permissions.remove_user([john, mary], ['view', 'edit'])

        """
        self._set_permissions('remove', perms, 'users', self._fetch_users(user))

    def add_group(self, group, perms):
        """Add ``perms`` permissions to ``group``.

        ``group`` can be single ``Group`` object, group name, group id,
        or a list of previous items.

        Example:

        If you want to add ``view`` permission on a ``My Collection``
        to the group ``my_lab``, run following code:

        .. code-block:: python

            collection = res.collection.get(name='My Collection')
            collection.permissions.add_group('my_lab', 'view')

        For advanced use-cases we also support more complex syntax
        like:

        .. code-block:: python

            my_lab = res.group.get('my_lab')
            your_lab = res.group.get('your_lab')
            collection = res.collection.get(name='My Collection')
            collection.permissions.add_group([my_lab, your_lab], ['view', 'edit'])

        """
        self._set_permissions('add', perms, 'groups', self._fetch_group(group))

    def remove_group(self, group, perms):
        """Remove ``perms`` permissions from ``group``.

        ``group`` can be single ``Group`` object, group name, group id,
        or list of of previous items.

        Example:

        If you want to remove ``view`` permission on a
        ``My Collection`` from the group ``my_lab``, run following
        code:

        .. code-block:: python

            collection = res.collection.get(name='My Collection')
            collection.permissions.remove_group('my_lab', 'view')

        For advanced use-cases we also support more complex syntax
        like:

        .. code-block:: python

            my_lab = res.group.get('my_lab')
            your_lab = res.group.get('your_lab')
            collection = res.collection.get(name='My Collection')
            collection.permissions.remove_group([my_lab, your_lab], ['view', 'edit'])

        """
        self._set_permissions('remove', perms, 'groups', self._fetch_group(group))

    def add_public(self, perms):
        """Add ``perms`` permissions to public user.

        Example:

        If you want to make ``My Collection`` public, run following
        code:

        .. code-block:: python

            collection = res.collection.get(name='My Collection')
            collection.permissions.add_public('view')

        """
        self._set_permissions('add', perms, 'public')

    def remove_public(self, perms):
        """Remove ``perms`` permissions from public user.

        Example:

        If you want to remove public permission form ``My Collection``,
        run following code:

        .. code-block:: python

            collection = res.collection.get(name='My Collection')
            collection.permissions.remove_public('view')

        """
        self._set_permissions('remove', perms, 'public')

    def _get_perms_by_type(self, perm_type):
        """Return only permissions with ``perm_type`` type."""
        return [perm for perm in self._permissions if perm['type'] == perm_type]

    def _perms_to_string(self, perms):
        """Return string representation of given permissions array."""
        perms = copy.copy(perms)

        # Order known permissions by importance.
        for known_perm in ['owner', 'share', 'edit', 'add', 'download', 'view']:
            if known_perm in perms:
                perms.remove(known_perm)
                perms.insert(0, known_perm)

        return ', '.join(perms)

    def __repr__(self):
        """Show permissions."""
        self.fetch()

        res = []

        public_perms = self._get_perms_by_type('public')
        if public_perms:
            res.append('Public: {}'.format(self._perms_to_string(public_perms[0]['permissions'])))

        user_perms = self._get_perms_by_type('user')
        if user_perms:
            res.append('Users:')
            for perm in user_perms:
                res.append(' - {} (id={}): {}'.format(
                    perm['name'], perm['id'], self._perms_to_string(perm['permissions'])
                ))

        group_perms = self._get_perms_by_type('group')
        if group_perms:
            res.append('Groups:')
            for perm in group_perms:
                res.append(' - {} (id={}): {}'.format(
                    perm['name'], perm['id'], self._perms_to_string(perm['permissions'])
                ))

        return '\n'.join(res)
