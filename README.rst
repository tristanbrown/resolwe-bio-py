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


Resolwe_ is a dataflow package for the `Django framework`_.
`Resolwe Bioinformatics`_ is an extension of Resolwe that provides
bioinformatics pipelines. Resolwe SDK for Python supports writing
dataflow pipelines for Resolwe and Resolwe Bioinformatics.

.. _Resolwe Bioinformatics: https://github.com/genialis/resolwe-bio
.. _Resolwe: https://github.com/genialis/resolwe
.. _Django framework: https://www.djangoproject.com/

Docs & Help
===========

Read the detailed description in documentation_.

.. _documentation: http://resolwe-bio-py.readthedocs.io/

Install
=======

Install from PyPI::

  pip install resdk

To install for development, `fork on Github`_ and run::

  git clone https://github.com/<GITHUB_USER>/resolwe-bio-py.git
  cd resolwe-bio-py
  pip install -e .[docs,package,test]

.. _fork on Github: https://github.com/genialis/resolwe-bio-py

Quick Start
===========

Connect to a Resolwe server:

.. code-block:: python

   from resdk import Resolwe
   re = Resolwe('admin', 'admin', 'https://torta.bcm.genialis.com')

Get sample by ID and download the aligned reads (BAM file):

.. code-block:: python

   sample = re.sample.get(1)
   sample.download(type='bam')

Find human samples and download all aligned reads (BAM files):

.. code-block:: python

   samples = re.sample.filter(descriptor__organism="Homo sapiens")
   for sample in samples:
       sample.download(type='bam')

Primary analysis (*e.g.,* filtering, alignment, expression estimation)
starts automatically when samples are annotated. A step in primary
analysis is represented as ``Data`` object, attached to the sample.
A ``Sample`` object includes sample annotation. A ``Data`` object
includes input parameters, results and analysis annotation. Print the
steps in primary analysis pipeline:

.. code-block:: python

    for data_id in sample.data:
        data = re.data.get(data_id)
        print data.process_name

Find ROSE2 analysis results and display a ??? plot of the first result:

.. code-block:: python

   rose2 = re.data.filter(type='data:chipseq:rose2:')
   # TODO: Plot results

Run Bowtie2 mapping on the reads ``Data`` object of the above sample:

.. code-block:: python

   genome = re.data.filter(type='data:genome:fasta:')[0]
   reads = sample.data[0]
   aligned = re.run('alignment-bowtie-2-2-3_trim', input={
                        genome: genome.id,
                        reads: reads.id,
                        reporting: {rep_mode: 'k', k_reports: 1}
                    })
   aligned.status()

Continue in the `Getting Started`_ section of Documentation, where we
explain how to upload files, create samples and provide details about
the Resolwe backend. Bioinformaticians can learn how to develop
pipelines in `Writing Pipelines`_.

.. _Getting Started: http://resdk.readthedocs.io/en/latest/intro.html
.. _Writing Pipelines: http://resdk.readthedocs.io/en/latest/pipelines.html
