.. _tutorial-resources:

==============================
Resources and advanced queries
==============================

In this tutorial you will learn the fundamentals of Resolwe, and revisit in
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
or about `Python logging`_ in general. 

.. _`Python logging`: https://docs.python.org/2/howto/logging.html
.. _`Genialis Platform`: https://app.genialis.com

Resources
=========

In Resolwe, meta-data is stored in the PostgreSQL database tables:
Data, Sample, Collection, Process, DescriptorSchema, Storage,
User, and Group. We support data management through the `REST API`_.
Each table is represented as a REST resource with a corresponding
endpoint. The Sample table is a special case, represented by the ``sample`` 
resource. More details on samples will be given later.

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
A Process stores an algorithm that transforms inputs into outputs. It
is a blueprint for one step in the analysis. A Data object is an
instance of a Process. It is a complete record of the process step. 
It remembers the inputs (files, arguments, parameters...), the process
(the algorithm) and the outputs (files, images, numbers...). In
addition, Data objects store some useful meta data, making it
easy to reproduce the dataflow and access information.

**Example use case:** you have a file with NGS read sequences
(``mouse-example-chr19.fastq``) and want to map them to the mouse genome
(``mm10_chr19.fasta``) with the *Bowtie* aligner. All you have to do is
create a Data object, setting the process and inputs. When the Data object
is created, the platform automatically runs the given process with
provided inputs, storing all inputs, outputs, and meta data. 

You have already seen how to create and query data objects in the 
`Download, upload, and annotations tutorial`_. 
You will learn the details of running processes to generate new data objects in
the `Running processes tutorial`_. For now,
let's just inspect the Bowtie process to learn a little more about it:

.. _Download, upload, and annotations tutorial: tutorial-upload.html

.. _Running processes tutorial: tutorial-running-processes.html

.. code-block:: python

    # Get the Bowtie process
    bowtie_process = res.process.get('alignment-bowtie2')

    # Access the process' `description` attribute
    bowtie_process.description

.. note::

   In the documentation we will refer to "process" in two different
   contexts. The first has just been presented: the blueprint for
   data objects. In this respect, a Data object is an instance of a
   Process. However, when talking about a specific data object, we
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
Typically, a sample would contain the following data: raw reads,
aligned reads, and expressions. Two distinct samples cannot
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

Samples
-------

When a new data object that represents a biological sample (i.e. fastq files,
bam files) is uploaded to the database, the unannotated sample is
automatically created. It is the duty of the researcher to properly
`annotate the sample`_. When a data object that belongs to an existing sample
is used as an input to trigger a new analysis, the output of this process is
automatically attached to an existing sample.

.. _annotate the sample: tutorial-upload.html

Once a sample is created, we can access it and all of the data associated with
it via the ``sample`` property:

.. code-block:: python

    # Access the sample associated with a reads data object
    new_sample = reads.sample

    # View all of the data associated with a sample
    new_sample.data

We can also access and change sample attributes like ``name`` or ``slug``:

.. code-block:: python

    #change sample name and slug
    new_sample.name = 'My sample 2'
    new_sample.slug = 'my-sample-2'
    new_sample.save()

Collections
-----------

To keep our data objects and samples organized, we can create collections.
Here is an example of how to create a new collection, modify its attributes,
and add or remove data:

.. code-block:: python

    # create a new collection object in your running instance of Resolwe (res)
    test_collection = res.collection.create(name='Test collection')

    # change the collection name
    test_collection.name = 'Test collection 5'

    # change the collection slug
    test_collection.slug = 'test-collection-5'

    # save new collection to the server you've accessed in your Resolwe instance
    test_collection.save()

    # add data to collection
    test_collection.add_data(reads)

    # remove data to collection
    test_collection.remove_data(reads)

Data objects can also be added to collections when running a process, as
described in following chapter on `the Run method`_.

.. _the Run method: tutorial-running-processes.html

Querying resources
==================

To get a list of data objects or samples stored in a collection, or
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

.. code-block:: python

    # Filter processes by the contributer
    res.process.filter(contributor=1)

    # Filter data by status
    res.data.filter(status='OK')

But the real power of the ``filter()`` method is in combining multiple filter
parameters:

.. code-block:: python

   # Filter data by several fields
    res.data.filter(
        status='OK',
        process_name='Bowtie 1.0.0',
        ordering='created',
        limit=3,
        )

.. TODO: Filter by process_name is broken.
    (https://github.com/genialis/resolwe-bio-py/issues/145)

In a single line we have obtained the first three data objects that were
successfully created (no errors) using the process with name "Aligner
(Bowtie 1.0.0)," ordered by creation time.

The :any:`get()<ResolweQuery.get>` method searches by the same parameters as
``filter`` and returns a single object of type ``<resource>``. If only one
parameter is given, it will be interpreted as a unique identifier ``id`` or
``slug``, depending on if it is a number or string.

.. code-block:: python
   
    # Get a Collection object by id
    res.collection.get(128)

    # Get a Sample by slug
    res.sample.get('mouse-example-chr19')

For the most-used filtering options, we created following shortcuts, which give
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

.. code-block:: python

    # Query a data object
    data = res.data.get(21887)

    # See the data object's type
    data.process_type

    # Filter data objects by type
    res.data.filter(type='data:genome:fasta:')

The following are some examples of filtering of collections, samples and data
objects:

.. TODO: Does `__in` not work?

.. code-block:: python

    # select collection with name 'Test collection'
    test_collection = res.collection.get(name='Test collection 0')

    # list of samples in 'Test collection 0'
    sample_list = test_collection.samples

    # list of data in my collection
    test_collection.data

    # list of data in samples that starts with 'case' that is part of
    'Test collection 0'
    sample_list.filter(name__startswith='Mouse')

    # get list of two data objects with following names: 'reads-1', 'reads-2':
    res.data.filter(name__in=['reads-1', 'reads-2'])

    # get list of data that were modified in year 2018 or later
    res.data.filter(modified__year__gte=2018)

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

.. TODO: Make a helper function for .__dict__.keys()

.. code-block:: python

    # Access a resource attribute
    res.<resource>.<attribute>
    
    # See a list of a resource's available attributes
    res.<resource>.__dict__.keys()

    # Get a sample by slug
    sample = res.sample.get('mouse-example-chr19')

    # Access the sample name
    sample.name

    # Access the creation date
    sample.created

    # Get the Bowtie process
    bowtie_process = res.process.get('alignment-bowtie2')

    # Access the process' permissions
    bowtie_process.permissions

Aside from these attributes, each resource class has some specific attributes
and methods. For example, resource classes ``Data``, ``Sample``, and
``Collection`` have the methods ``files()`` and ``download()``.

The ``files()`` method returns a list of all files on the resource:

.. code-block:: python

    # Get data by slug
    data = res.data.get('mouse-example-chr19')

    # Print a list of files
    data.files()

    # Filter the list of files by file name
    data.files(file_name='mouse-example-chr19-2.fastq.gz')

    # Filter the list of files by field name
    data.files(field_name='output.fastq')

The method ``download()`` downloads the resource files. The optional parameters
``file_name`` and ``field_name`` have the same effect as in the ``files``
method. There is an additional parameter, ``download_dir``, that allows you to
specify the download directory:

.. code-block:: python

    # Get sample by slug
    sample = res.sample.get('mouse-example-chr19')

    # Download the NGS reads file
    sample.download(
        file_name='mouse-example-chr19-2.fastq.gz',
        download_dir='/path/to/target/dir/'
        )

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
