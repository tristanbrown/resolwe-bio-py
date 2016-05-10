=================================
Resolwe Bioinformatics Python API
=================================

|build| |docs| |pypi_version| |pypi_pyversions| |pypi_downloads|

.. |build| image:: https://travis-ci.org/genialis/resolwe-bio-py.svg?branch=master
    :target: https://travis-ci.org/genialis/resolwe-bio-py
    :alt: Build Status

.. |docs| image:: https://readthedocs.org/projects/resolwe-bio-py/badge/?version=latest
    :target: http://resolwe-bio-py.readthedocs.io/
    :alt: Documentation Status

.. |pypi_version| image:: https://img.shields.io/pypi/v/resolwe-bio-py.svg
    :target: https://pypi.python.org/pypi/resolwe-bio-py
    :alt: Version on PyPI

.. |pypi_pyversions| image:: https://img.shields.io/pypi/pyversions/resolwe-bio-py.svg
    :target: https://pypi.python.org/pypi/resolwe-bio-py
    :alt: Supported Python versions

.. |pypi_downloads| image:: https://img.shields.io/pypi/dm/resolwe-bio-py.svg
    :target: https://pypi.python.org/pypi/resolwe-bio-py
    :alt: Number of downloads from PyPI


Python API for `Resolwe Bioinformatics`_—Bioinformatics pipelines for the
Resolwe_ dataflow package for `Django framework`_.

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

  python setup.py install

To install for development, run::

  python setup.py develop


Usage
=====

Create an API instance:

.. code-block:: python

   from resolwe_api import Resolwe
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
