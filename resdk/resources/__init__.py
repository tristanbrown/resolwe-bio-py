""".. Ignore pydocstyle D400.

=========
Resources
=========

Resource classes
================

.. autoclass:: resdk.resources.base.BaseResource
   :members:

.. autoclass:: resdk.resources.Data
   :members:

.. autoclass:: resdk.resources.collection.BaseCollection
   :members:

.. autoclass:: resdk.resources.Collection
   :members:

.. autoclass:: resdk.resources.Sample
   :members:

.. autoclass:: resdk.resources.Process
   :members:

Utility functions
=================

.. automodule:: resdk.resources.utils
   :members: iterate_fields, iterate_schema, find_field, fill_spaces

"""

from .collection import Collection, get_collection_id
from .data import Data, get_data_id
from .sample import Sample, get_sample_id
from .process import Process, get_process_id

__all__ = ('get_collection_id', 'get_data_id', 'get_sample_id', 'get_process_id',
           'Collection', 'Data', 'Sample', 'Process')
