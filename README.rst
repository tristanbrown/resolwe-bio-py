======================
Resolwe SDK for Python
======================

|build| |docs| |pypi_version| |pypi_pyversions| |pypi_downloads|

.. |build| image:: https://travis-ci.org/genialis/resolwe-bio-py.svg?branch=master
    :target: https://travis-ci.org/genialis/resolwe-bio-py
    :alt: Build Status

.. |docs| image:: https://readthedocs.org/projects/resdk/badge/?version=latest
    :target: http://resdk.readthedocs.io/
    :alt: Documentation Status

.. |pypi_version| image:: https://img.shields.io/pypi/v/resdk.svg
    :target: https://pypi.python.org/pypi/resdk
    :alt: Version on PyPI

.. |pypi_pyversions| image:: https://img.shields.io/pypi/pyversions/resdk.svg
    :target: https://pypi.python.org/pypi/resdk
    :alt: Supported Python versions

.. |pypi_downloads| image:: https://img.shields.io/pypi/dm/resdk.svg
    :target: https://pypi.python.org/pypi/resdk
    :alt: Number of downloads from PyPI


The Resolwe SDK for Python supports writing tools for Resolwe_ dataflow
package for `Django framework`_ and `Resolwe Bioinformatics`_ that
includes the bioinformatics pipelines.

.. _Resolwe Bioinformatics: https://github.com/genialis/resolwe-bio
.. _Resolwe: https://github.com/genialis/resolwe
.. _Django framework: https://www.djangoproject.com/

Docs & Help
===========

Read detailed description in the documentation_.

.. _documentation: http://resolwe-bio-py.readthedocs.io/


Install
=======

To install, run::

  pip install resdk

To install for development, run::

  pip install -e .[docs,package,test]


Usage
=====

Connect to the Resolwe server:

.. code-block:: python

   from resdk import Resolwe
   re = Resolwe('me@mail.com', 'my_password', 'www.resolwe.com')

Get all collections and select the first one:

.. code-block:: python

   collections = re.collections()
   collection = list(collections.values())[0]

Get expression objects and select the first one:

.. code-block:: python

   expressions = collection.data(type__startswith='data:expression:')
   expression = expressions[0]

Print annotation:

.. code-block:: python

   expression.print_annotation()

Print file fields:

.. code-block:: python

   expression.print_downloads()

Download file:

.. code-block:: python

   filename = expression.annotation['output.exp']['value']['file']
   file_stream = expression.download('output.exp')
   with open(filename, 'w') as f:
       for part in file_stream:
           f.write(part)
