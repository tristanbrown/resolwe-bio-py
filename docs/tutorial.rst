========
Tutorial
========

This tutorial is intended to guide a first-time user through the set-up of the Resolwe Python SDK for bioinformatics pipeline development. We will show how to connect to a Resolwe server, upload a BAM file and identify a chromosome with the most aligned reads. Before we begin, make sure you have SSH access to the `Torta server`_.

.. _Torta server: https://torta.bcm.genialis.com

Install SDK
===========

To set-up the Resolwe Python SDK, follow the :doc:`installation instructions.<contributing>`

Usage
=====

Set the ``TOOLS_REMOTE_HOST`` environment variable in your terminal:

.. code-block:: bash

	export TOOLS_REMOTE_HOST=<username>@torta.bcmt.bcm.edu://genialis/tools

In the same terminal window, create a connection to the Resolwe server using Python:


.. code-block:: python

	python
	import resdk
	res = resdk.Resolwe('admin', 'admin', 'https://torta.bcm.genialis.com')
	resdk.start_logging()

Upload a BAM file using an `upload-bam`_ processor:

.. _upload-bam: https://github.com/genialis/resolwe-bio/blob/master/resolwe_bio/processes/import_data/bam.yml

.. code-block:: python

	bam = res.run("upload-bam", input={'src': '/path/to/file/test.bam'})

What just happened? We have assigned a BAM file path to the processor's input field ``src``. The process ``upload-bam`` of type ``data:alignment:bam:upload`` has a defined set of input (``src``) and output (``bam``, ``bai``) fields, together with an algorithm to transform inputs into outputs. In the case of the ``upload-bam`` process, BAM file is uploaded, indexed using ``samtools``, and saved into output fields ``bam`` and ``bai``, respectively. For a list of all available processes, please see the `Resolwe Bio Documentation`_.

.. _Resolwe Bio Documentation: http://resolwe-bio.readthedocs.io

Check the processing status of the bam object:

.. code-block:: python

	bam.update()
	bam.status

Status ``OK`` indicates the processing has finished successfuly. Processing details can be inspected by:

.. code-block:: python

	print(bam.stdout())

Uploaded BAM file can now be used for further processing steps in any other processes that are using a compatible input type ``data:alignment:bam:upload`` or its subtypes (e.g. ``data:alignment:bam``).

We will now define a new processor that takes uploaded BAM file as an input and reports the name of the chromosome with the largest number of aligned reads:

.. code-block:: yaml

	- slug: max-reads
	  name: Max reads
	  data_name: Chromosome (max reads)
	  version: 1.0.0
	  type: data:bam:stats
	  input:
	    - name: bam
	      label: BAM file
	      type: data:alignment:bam
	  output:
	    - name: stats
	      label: Stats
	      type: basic:file
	    - name: chr
	      label: Chr (max reads)
	      type: basic:string
	  run:
	    runtime: polyglot
	    bash: |
	      samtools idxstats {{bam.bam.file}} > stats.txt
	      re-save-file stats stats.txt
	      CHR=`<my_script>.py stats.txt`
	      re-save chr "${CHR}"

Save the above code to a file ``<processor_name>.yaml`` using a text editor. **Make sure to modify the name of the Python script** ``<my_script>.py`` **that is referenced in the above code**. **You will create this** ``.py`` **file in the next step**. Analysis steps can include tools available from the Biolinux-based `docker container`_ (e.g. ``samtools``) or custom scripts (e.g. Python, R) defined by the user. We have designed the above processor ``<processor_name>.yaml`` to use the custom script ``<my_script>.py`` to parse the ``samtools idxstats`` results file and report the chromosome name:

.. _docker container: https://github.com/genialis/docker-bio-linux8-resolwe

.. code-block:: python

	#!/usr/bin/env python2
	import sys

	fname = sys.argv[1]

	max_reads = 0
	chromosome = ''

	with open(fname) as file:
	    for line in file:
	        if line.startswith('chr'):
	            stats = line.split('\t')
	            if int(stats[2]) > max_reads:
	                max_reads = int(stats[2])
	                chromosome = stats[0]

	print chromosome

Save the above code to a file ``<my_script>.py`` and mark it as an executable script.

.. code-block:: bash

	chmod +x <my_script>.py

We are now ready to use an uploaded BAM file object (``bam``) as an input to a new processor that was just defined:

.. code-block:: python

	chr = res.run("max-reads", input={'bam': bam.id}, src="/path/to/<processor_name>.yaml", tools=['/path/to/<my_script>.py'])

Again, we can inspect the status of the processing step by:

.. code-block:: python

	chr.update()
	chr.status
	print(chr.stdout())

We can see the analysis results by inspecting the ``chr`` object's ``output`` fields:

.. code-block:: python

	chr.output

The name of the chromosome with the most aligned reads is saved in the ``chr`` output field. Results file saved into the ``stats`` field can be downloaded by:

.. code-block:: python

	chr.download()
