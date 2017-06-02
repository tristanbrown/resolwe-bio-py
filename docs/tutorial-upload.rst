.. _tutorial-upload:

===========================
Data upload and annotations
===========================

Run the Python interpreter (type ``python`` in the terminal) and connect
to the Genialis Platform:

.. literalinclude:: files/example_index.py
   :lines: 1-7

Upload fastq files
==================

Various bioinformatic processes are available to properly analyse genetic
data. Many of these pipelines are prepared to use with Resolwe
SDK and listed in the `Process catalog`_ of the `Resolwe Bioinformatics documentation`_.

.. _Process catalog: http://resolwe-bio.readthedocs.io/en/latest/catalog.html
.. _Resolwe Bioinformatics documentation: http://resolwe-bio.readthedocs.io

To begin this Tutorial with upload of fastq single ends reads with `upload-fastq-single`_ processor or fastq
paired ends reads with `upload-fastq-paired`_ processor.

.. _upload-fastq-single: http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-upload-fastq-single
.. _upload-fastq-paired: http://resolwe-bio.readthedocs.io/en/latest/catalog-definitions.html#process-upload-fastq-paired

.. code-block:: python

    # Upload a fastq single reads
    reads = res.run('upload-fastq-single', input={'src': '/path/to/reads.fastq'})

    # Upload a fastq paired reads
    reads_paired = res.run('upload-fastq-paired', input={'src1': ['/path/to/reads.fastq_1'], 'src2': ['/path/to/reads.fastq_2']})

What just happened? Firstly we defined which process we would like to run, with its
slug ``upload-fastq-single`` or ``upload-fastq-paired``. Secondly we have assigned
a fastq file path to the process' input field ``src``.
Each process has a defined set of input and output fields. Inputs should be
given at execution.

Uploading a fastq file creates an object that can be referenced by ID or slug.
This objects can have annotations that are used in searches.
You can annotate the reads, using reads descriptor schema which is described in
the Annotations chapter.

Annotations
===========

Annotations are presented as descriptors, where each descriptor is defined in
descriptor schemas. Annotations for data objects, samples and collections are
following different descriptor schemas. For example reads data object can be
annotated with 'reads' descriptor schema, while sample can be annotated by
'sample' annotation schema. Each data object that is part of sample is
also connected to sample annotation, so that the annotation for sample (also
collection) represents all Data objects attached to it. Examples of descriptors
and descriptor schemas are described in details in `Resolwe Bioinformatics
documentation`_.

.. _Resolwe Bioinformatics documentation: http://resolwe-bio.readthedocs.io

Here we show how to annotate the reads data object by defining a descriptor
information (annotation) that follows annotation fields as defined in the
'reads' descriptor schema:

.. code-block:: python

    annotation_reads = {
        'experiment_type': 'RNA-seq',
        'protocols': {
            'growth_protocol': 'my growth protocol',
            'treatment_protocol': 'my treatment protocol',
            'library_prep': 'lybrary construction protocol',
        },
        'reads_info': {
            'seq_date': '2016-10-13',
            'instrument_type': 'Illumina',
            'facility': 'my favorite facility',
        }
    }

We can now annotate ``reads`` data object by adding descriptor and descriptor schema:

.. TODO: Check if the example works and provide a full working example

.. code-block:: python

    #define the chosen descriptor schema,
    reads.descriptor_schema = 'reads'

    #define the reads descriptor, with
    reads.descriptor = annotation_reads

    #save the annotation
    reads.save()

We can also define descriptor and descriptor schema directly when calling
'res.run' function as described in The run method section.
