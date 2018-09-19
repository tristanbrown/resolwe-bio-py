.. _tutorial-upload:

======================================
Data download, upload, and annotations
======================================

To gain a more in-depth understanding of the vast functionality of the ReSDK
API, we first need to get some data on the Resolwe servers that we can work
with. Run the Python interpreter (type ``python`` in the terminal) and connect
to the Genialis Platform:

.. literalinclude:: files/example_index.py
   :lines: 1-7

Upload fastq files
==================

Various bioinformatic processes are available to properly analyze genetic
data. Many of these pipelines are available via Resolwe SDK, and are listed in
the `Process catalog`_ of the `Resolwe Bioinformatics documentation`_.

.. _Process catalog: http://resolwe-bio.readthedocs.io/en/latest/catalog.html
.. _Resolwe Bioinformatics documentation: http://resolwe-bio.readthedocs.io

To begin, we need some sample data to work with. You may use your own reads
(.fastq) files, or download an example set we have provided:

.. code-block:: python

    # Get a tutorial sample
    example = res.sample.get(347)

    # Download the reads files and meta-data
    example.download(download_dir='/path/to/target/dir/')

We can upload fastq single end reads with the `upload-fastq-single`_
process, or fastq paired ends reads with the `upload-fastq-paired`_ process.

.. _upload-fastq-single: http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-upload-fastq-single
.. _upload-fastq-paired: http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-upload-fastq-paired

.. code-block:: python

    # Upload a fastq single reads
    reads = res.run(
        'upload-fastq-single',
        input={'src': '/path/to/reads.fastq'}
    )

    # Upload a fastq paired reads
    reads = res.run(
        'upload-fastq-paired',
        input={
            'src1': '/path/to/reads-1.fastq.gz',
            'src2': '/path/to/reads-2.fastq.gz'
        }
    )

What just happened? First, we chose a process to run, using
its slug ``upload-fastq-single`` or ``upload-fastq-paired``. Second, we have
assigned a fastq file path to the process' input field ``src``. Each process has
a defined set of input and output fields. Inputs should be given at execution.

Uploading a fastq file creates a data object that can be referenced by ID or
slug. You can immediately see these identifiers for your newly uploaded data
object by entering ``reads``. If you exit your python
interpreter session, the ``reads`` variable will no longer be saved, but the
data is still on the server, allowing you to query it again:

.. code-block:: python

    # View the data object's identifiers
    reads

    # Query the data object again, after closing the interpreter
    reads = res.data.get(<id or slug>)

The upload process also created a sample object for the reads data to be
associated with. You will learn more about samples in later tutorials, but for
now, it's sufficient to understand how to query the one you've created:

.. code-block:: python

    # Query the sample you've created
    new_sample = reads.sample

    # View the sample object's identifiers
    new_sample

    # Query the sample object again, after closing the interpreter
    sample = res.sample.get(<id or slug>)

.. TODO: When filter-by-contributor-username is possible, rewrite the next
    section.

Every time you upload a data object to the Resolwe servers, you are marked
as the contributor of both the data and the sample objects that have been
created. If you know your user ``id``, you can search for all of the objects
that you've created on the server:

.. code-block:: python

    # See the id, username, first name, and last name of the data contributor
    reads.contributor

    # Shows the same information
    new_sample.contributor

    # Find the data objects you've contributed
    res.data.filter(contributor=<your id>)

    # Find the samples you've contributed
    res.sample.filter(contributor=<your id>)

.. note::

    Please record your user ``id`` number for future reference.

These objects can be given annotations that are used in
searches, using the reads and sample descriptor schema described below.

Annotations
===========

Annotations are encoded as bundles of descriptors, where each descriptor
references a value in a descriptor schema (i.e. a template). Annotations for
data objects, samples, and collections each follow a different descriptor
format. For example, a reads data object can be annotated with the 'reads'
descriptor schema, while a sample can be annotated by the 'sample' annotation
schema. Each data object that is associated with the sample is also connected to
the sample's annotation, so that the annotation for a sample (or collection)
represents all Data objects attached to it. `Descriptor schemas`_ are described
in detail (with `accompanying examples`_) in the `Resolwe Bioinformatics
documentation`_.

.. _Resolwe Bioinformatics documentation: http://resolwe-bio.readthedocs.io
.. _Descriptor schemas: http://resolwe-bio.readthedocs.io/en/stable/descriptor.html
.. _accompanying examples: https://github.com/genialis/resolwe-bio/tree/master/resolwe_bio/descriptors

Here, we show how to annotate the ``reads`` data object by defining the
descriptor information that populates the annotation fields as defined in the
'reads' descriptor schema:

.. code-block:: python

    annotation_reads = {
        'experiment_type': 'RNA-seq',
        'protocols': {
            'growth_protocol': 'my growth protocol',
            'treatment_protocol': 'my treatment protocol',
            'library_prep': 'library construction protocol',
        },
        'reads_info': {
            'seq_date': '2016-10-13',
            'instrument_type': 'Illumina',
            'facility': 'my favorite facility',
        }
    }


We can now annotate the ``reads`` data object by adding the descriptor
schema and the desired information:

.. code-block:: python

    #define the chosen descriptor schema,
    reads.descriptor_schema = 'reads'

    #define the reads descriptor, with
    reads.descriptor = annotation_reads

    #save the annotation
    reads.save()

We can annotate the sample object using a similar process with a 'sample'
descriptor schema:

.. code-block:: python

    annotation_sample = {
        'sample': {
            'annotator': 'my name',
            'organism': 'Mus musculus',
            'source': 'Hippocampus',
            'strain': 'F1 hybrid FVB/N x 129S6/SvEv',
            'molecule': 'total RNA',
            'genotype': 'your mouse variant',
            'cell_type': 'glioblastoma',
            'optional_char': ['my_characteristic:{}'.format('value')],
            'description': 'any additional description',
        },
        'other': {'notes': 'any other information'},
    }

.. warning::

    Many descriptor schema have required fields with a limited set of choices
    that may be applied as annotations. For example, the 'organism' annotation
    in a sample descriptor must be selected from the list of options in the
    `sample descriptor schema`_, represented by its Latin name.

.. _sample descriptor schema: https://github.com/genialis/resolwe-bio/blob/master/resolwe_bio/descriptors/sample_geo.yml

Now apply the annotation to the sample:

.. code-block:: python

    #define the chosen descriptor schema,
    new_sample.descriptor_schema = 'sample'

    #define the sample descriptor, with
    new_sample.descriptor = annotation_sample

    #save the annotation
    new_sample.save()

We can also define descriptors and descriptor schema directly when calling
'res.run' function as described in the `run method section`_.

.. _run method section: http://resdk.readthedocs.io/en/stable/ref.html#resolwe

In this tutorial, you have learned how to upload and annotate objects on the
Resolwe servers using ReSDK. Next, we will learn some powerful tools for
organizing and analyzing these objects.
