.. _tutorial-resources:

==============================
Resources and advanced queries
==============================

In this tutorial you will learn basic concepts about Resolwe, and revisit in
more detail some of the tools we have already discussed. For this tutorial, it
is helpful (but not required) to have a working understanding of
`Python class objects`_.

`Resolwe`_ is an open source dataflow package for the
`Django framework`_. `Resolwe Bioinformatics`_ is an extension of
Resolwe that provides bioinformatics pipelines. Together, they can
handle large quantities of biological data, perform complex data
analysis, organize results, and automatically document your work in
a reproducible fashion.

Resolwe SDK for Python allows you to access Resolwe and Resolwe Bio through
Python. It supports accessing, modifying, uploading, and downloading the
data, and writing dataflow pipelines.

.. _Resolwe Bioinformatics: https://github.com/genialis/resolwe-bio
.. _Resolwe: https://github.com/genialis/resolwe
.. _Django framework: https://www.djangoproject.com/
.. _Python class objects: https://docs.python.org/3/tutorial/classes.html

.. figure:: images/resolwe_resdk.jpg
   :width: 100 %

Resolwe and Resolwe Bio run on servers with strong computational
capabilities. We will use a public Resolwe server `Genialis Platform`_
that is configured for the examples in the tutorial. ``resdk`` is a
Python package on a local computer that interacts with Resolwe through
a RESTful API. The power of ``resdk`` is its lightweight character.
It is installed with one simple command, but supports the manipulation
of large data sets and heavy computation on a remote computer cluster.
Let's connect to the Genialis Platform server.

.. literalinclude:: files/example_index.py
   :lines: 1-7

If you are working with ``resdk`` in an interactive session, the
logging feature prints useful messages. It will let you know
what is happening behind the scenes. Read more about
:ref:`how the logging is configured in resdk<resdk_resdk_logger>`
or about `Python logging`_ in general. Now let's access some reads data. 

.. _`Python logging`: https://docs.python.org/2/howto/logging.html
.. _`Genialis Platform`: https://app.genialis.com

.. code-block:: python

    # See reads data objects available to you on the server
    res.data.filter(type='data:reads')

    # Get a reads data object by ID number
    reads = res.data.get(<ID>)

.. TODO: Choose a reads object the user can use throughout this tutorial.

Resources
=========

In Resolwe, meta-data is stored in the PostgreSQL database tables:
Data, Sample, Collection, Process, DescriptorSchema, Storage,
User, and Group. We support data management through the `REST API`_.
Each table is represented as a REST resource with a corresponding
endpoint. The Sample table is a special case, represented by two
resources: ``sample`` and ``presample``. More details on samples will
be given later.

In ``resdk`` each REST API endpoint has a corresponding class, with
the same name as in Resolwe: :class:`Process<resdk.resources.Process>`,
:class:`Data<resdk.resources.Data>`,
:class:`Sample<resdk.resources.Sample>` and
:class:`Collection<resdk.resources.Collection>`. Most resources
are implemented in resdk as subclasses of
:class:`BaseResource<resdk.resources.base.BaseResource>`.

.. _REST API: https://torta.bcm.genialis.com/api/

Data and Processes
------------------

The two most important resources in Resolwe are *process* and *data*.
A process stores an algorithm that transforms inputs into outputs. It
is a blueprint for one step in the analysis. A Data object is an
instance of a process. It is a complete record of the process step. 
It remembers the inputs (files, arguments, parameters...), the process
(the algorithm) and the outputs (files, images, numbers...). In
addition, Data objects store some useful meta data. This makes it
easy to reproduce the dataflow as well as simply access information.

**Example use case:** you have a file with NGS read sequences
(``reads.fastq``) and want to map them to the human genome
(``hg38.fasta``) with the *Bowtie* aligner. All you have to do is
create a Data object, setting the process and inputs. When the Data object
is created, the platform automatically runs the given process with
provided inputs, storing all inputs, outputs, and meta data. 

.. TODO: show code for creating a Data object with the given process. \
    Give a clear, step-by-step workflow walkthrough. 

.. note::

   In the documentation we will refer to process in two different
   contexts. The first has just been presented: the blueprint for
   data objects. In this respect, data object is an instance of a
   process. However, when talking about specific data object, we
   may wish to refer to the algorithm that turned inputs to
   outputs---on this specific data object. We sometimes call
   this as a process as well.

Groups of Data objects
----------------------

Eventually, you will have many Data objects and want to
organize them. Resolwe includes different structures to help you group
Data objects: *Sample* and *Collection*.

**Sample** represents a biological entity. It includes user annotations
(GEO compliant) and Data objects associated with this biological entity.
In practice, all Data objects on the sample are derived from an initial
single Data object. A Data object can belong to only one sample.
Typically a sample would contain the following data: raw reads,
aligned reads, and expressions. Two distinct samples can not
contain the same Data object

**Collection** is a working (user-defined, *ad hoc*) group of samples.
In addition to samples and their data, collections may contain
Data objects that store analysis results (*e.g.,* differential
expressions). Samples and Data objects may be in multiple collections.

.. figure:: images/collections_relation.jpg
   :width: 100 %

   Relations between samples and collections. Samples
   are groups of Data objects originating from the same biological
   sample—all Data objects in a sample are derived from a single NGS
   reads file. Collections are arbitrary groups of samples
   and Data objects that store analysis results.

.. TODO: Image where clear distinction between Resolwe models /
         endpoints and resdk classes is presented.

Samples and presamples
----------------------

When a new data object that represents a biological sample (i.e. fastq files,
bam files) is uploaded to the database, the unannotated sample (presample) is
automatically created. When a data object that belongs to an existing (pre)sample
is used as an input to trigger new analysis, the output of the new analysis is
automatically attached to an existing (pre)sample.

Unannotated samples (presamples) have a presample property set to ``True``. To
annotate a presample, fill out its descriptor and set ``presample`` property to
``False``. Following is an example of annotation of presample, that was
automatically created when reads were uploaded.

.. code-block:: python

    annotation_sample = {
        'sample': {
            'annotator': 'my name',
            'organism': 'Homo sapiens',
            'source': 'isolated DNA',
            'cell_type': 'houman podocytes',
            'genotype': 'abcg2-',
            'molecule': 'total RNA',
            'optional_char': ['my_characteristic:{}'.format('value')],
            'description': 'any additional description',
            },
        'other': 'any other information',
    }

    # define presample name
    reads.presample.name = 'My favorite sample'

    #add descriptor schema to sample
    reads.presample.descriptor_schema = 'sample'

    # define presample description
    reads.presample.descriptor = annotation_sample

    # transform presample to sample
    reads.presample.presample = False

    #save presample as sample with the same name
    reads.presample.save()

.. note::
    Once a presample is marked as annotated, we can access it via the ``sample``
    property:

    .. code-block:: python

        reads.sample

Additionally, we can also confirm that the sample is annotated by changing the 
sample name or slug:

.. code-block:: python

    #change sample name and slug
    reads.sample.name = 'My sample 2'
    reads.sample.slug = 'my-sample-2'
    reads.sample.save()

Collections
-----------

To keep our data objects and samples organized, we can create collections.
Here is an example of how to create a new collection and add or remove data:

.. code-block:: python

    # import the Collection resource type from resdk.resources
    from resdk.resources import Collection

    # create a new collection object in your running instance of Resolwe (res)
    test_collection = Collection(resolwe=res)

    # name the collection
    test_collection.name = 'Test collection'

    #define the collection slug
    test_collection.slug = 'test-collection'

    #save new collection to the server you've accessed in your Resolwe instance
    test_collection.save()

    #add data to collection
    test_collection.add_data(reads)

    #remove data to collection
    test_collection.remove_data(reads)

Data objects can also be added to collections when running a process, as
described in following chapter on `the Run method`_.

.. _the Run method: http://resdk.readthedocs.io/en/stable/tutorial-running-processes.html

Querying resources
==================

To get a list of data objects, presamples or samples stored in a collection, or
to search for a specific type or name of data object, we can use a powerful and
convenient query system.

The :class:`resdk.Resolwe` class includes queries for the following object
types:

* ``process``
* ``data``
* ``sample``
* ``collection``

Each object type has a corresponding class in Resolwe. The interfaces support
``get()`` and ``filter()`` methods that enable users to access the resources:

.. code-block:: python

    resdk.Resolwe.<object_type>.filter(**fields)
    resdk.Resolwe.<object_type>.get(uid)

The :any:`filter(**fields)<ResolweQuery.filter>` method returns a list of
objects under the conditions defined by ``**fields``:

.. TODO: Explain filter(**fields) better

.. literalinclude:: files/example_intro.py
   :lines: 9-13

But the real power of the ``filter()`` method is in combining multiple filter
parameters:

.. literalinclude:: files/example_intro.py
   :lines: 15-16

In a single line we have obtained the first three data objects that were
successfully created (no errors) using the process with name "Aligner
(Bowtie 1.0.0)," ordered by creation time.

The :any:`get()<ResolweQuery.get>` method searches by the same parameters as
``filter`` and returns a single object of type ``<interface>``. If only one
parameter is given, it will be interpreted as a unique identifier ``id`` or
``slug``, depending on if it is a number or string.

.. literalinclude:: files/example_intro.py
   :lines: 3-7

For the most used filtering options we created following shortcuts, which give
us a list of `data`, `samples` or `collections`:

* ``<collection>.data``
* ``<collection>.samples``
* ``<sample>.data``
* ``<sample>.collections``
* ``<data>.collections``
* ``<data>.sample``

If we want to filter by a more specific type of data (e.g. reads), we can
indicate types (and optionally, subtypes) of data using
``data:<type>:<subtype>`` (e.g. ``data:reads``). You can see the type of a
dataset using the ``process_type`` attribute:

.. TODO: Include process_type example here. 

The following are some examples of filtering of collections, samples and data
objects:

.. TODO: Need better filter examples (e.g. by dates)
.. TODO: Need a complete list of data types
.. TODO: Does filter by contributor fail every time? 
.. TODO: Filtering samples seems to give everything. 

.. code-block:: python

    # select collection with name 'Test collection'
    test_collection = res.collection.get(name='Test collection')

    # list of samples in 'Test collection'
    sample_list = test_collection.samples

    # list of data in my collection
    test_collection.data

    # list of data in samples that starts with 'case' that is part of
    'Test collection'
    sample_list.filter(name__startswith='case')

    # get list of two data objects with following names: 'reads-1', 'reads-2':
    res.data.filter(name__in=['reads-1', 'reads-2'])

    # get list of data that were modified in year 2015 or later
    res.data.filter(modified__year__gte=2015)

    # select 'case_1' from 'my collection'
    case_1 = sample_list.get(name='case_1')

    # select 'case_1' bam file
    bam = case_1.data.get(type='data:alignment:bam:')

    # in which collections is sample 'case_1'
    list_collections = case_1.collections

    # in which collections is data 'bam'
    list_collections = bam.collections


More powerful query options are described in `SDK Reference`_

.. _SDK Reference: http://resdk.readthedocs.io/en/latest/ref.html


Accessing meta-data and downloading files
-----------------------------------------

We have learned how to query the resources with ``get``, ``filter``, or by using
shortcuts. Now we will look at how to access the information in these resources.
All of the resources share some common attributes like ``name``, ``id``,
``slug``, ``created``, and ``permissions``. You can access them like any other
Python class attributes.

.. literalinclude:: files/example_intro.py
   :lines: 18-31

Aside from these attributes, each resource class has some specific attributes
and methods. For example, resource classes ``Data``, ``Sample``, and
``Collection`` have the methods ``files()`` and ``download()``.

The ``files()`` method returns a list of all files on the resource:

 .. literalinclude:: files/example_intro.py
    :lines: 33-43

The method ``download()`` downloads the resource files. The optional parameters
``file_name`` and ``field_name`` have the same effect as in the ``files``
method. There is an additional parameter, ``download_dir``, that allows you to
specify the download directory:

.. literalinclude:: files/example_intro.py
   :lines: 45-49

You can find the complete reference for each resource class and their
corresponding attributes and methods in the :doc:`Reference<ref>`.

.. note::

   Some attributes and methods are defined in the
   :obj:`BaseResource<resdk.resources.base.BaseResource>`
   and :obj:`BaseCollection<resdk.resources.collection.BaseCollection>`
   classes. :obj:`BaseResource<resdk.resources.base.BaseResource>`
   is the parent of all resource classes in :obj:`resdk`.
   :obj:`BaseCollection<resdk.resources.collection.BaseCollection>`
   is the parent of all collection-like classes:
   :obj:`Sample<resdk.resources.Sample>` and
   :obj:`Collection<resdk.resources.Collection>`
