=================================
Resolwe Bioinformatics Python API
=================================

Python API for `Resolwe Bioinformatics`_—Bioinformatics pipelines for the
Resolwe_ dataflow package for `Django framework`_.

.. _Resolwe Bioinformatics: https://github.com/genialis/resolwe-bio
.. _Resolwe: https://github.com/genialis/resolwe
.. _Django framework: https://www.djangoproject.com/

Docs & Help
===========

Read detailed description in the documentation_.

.. _documentation: http://resolwe-bio-py.readthedocs.org/


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

   from genesis import Genesis
   gen = Genesis()


Get all project and select the first one:

.. code-block:: python

   projects = gen.projects()
   project = list(projects.values())[0]

Get expression objects and select the first one:

.. code-block:: python

   expressions = project.data(type__startswith='data:expression:')
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
   resp = expression.download('output.exp')
   with open(filename, 'w') as fd:
       fd.write(resp.content)
