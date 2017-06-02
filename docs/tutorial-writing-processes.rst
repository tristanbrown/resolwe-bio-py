.. _tutorial-writing:

=================
Writing processes
=================

Writing a new process
---------------------

You can write your own analysis processes that run on the server.
Let's write a process that takes a BAM object and reports which
chromosome has the largest number of aligned reads.

.. code-block:: yaml

    - slug: max-reads            # User readable unique identifier
      name: Max reads            # Process name
      requirements:
        expression-engine: jinja
      data_name: Chromosome      # The name of data objects created by the process
      version: 1.0.0             # Process version
      type: data:bam:stats       # The type of the process and data objects created by it
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
      run:                       # The algorithm in bash using Django template tags
        runtime: polyglot
        language: bash
        program: |
          # Compute sequence alignment statistics
          samtools idxstats {{bam.bam.file}} > stats.txt

          # Save the statistics file
          re-save-file stats stats.txt

          # Find chromosome with the largest number of aligned reads
          CHR=`<my_script>.py stats.txt`

          # Save the chromosome name
          re-save chr "${CHR}"

Set the ``TOOLS_REMOTE_HOST`` environment variable in your terminal:

.. code-block:: bash

    export TOOLS_REMOTE_HOST=<username>@torta.bcmt.bcm.edu://genialis/tools

This address will be used to automatically copy your scripts to the
Resolwe server. Make sure to set the ``TOOLS_REMOTE_HOST`` environment
variable in all terminal windows where you run Python.

Copy the above code to a file ``<process_name>.yaml``, use a text
editor. **Make sure to modify the name of the Python script**
``<my_script>.py`` **that is referenced in the above code**.
**You will create this Python script in the next step**. Analysis
steps can call programs installed in our `docker container`_ (`e.g.,`
``samtools``) and custom scripts (`e.g.,` Python and R) defined by the
user. We have designed the process ``<process_name>.yaml`` to use
a custom script ``<my_script>.py`` to parse the ``samtools idxstats``
results file and report the chromosome name.

.. _docker container: https://github.com/genialis/docker-bio-linux8-resolwe

.. code-block:: python

    #!/usr/bin/env python2
    import sys

    # Read the statistics file name from the command arguments
    fname = sys.argv[1]

    max_reads = 0
    chromosome = ''

    # Open the statistics file
    with open(fname) as file:
        # Iterate through lines
        for line in file:
            # Find lines with chromosome statistics
            if line.startswith('chr'):
                stats = line.split('\t')
                # Check if a chromosome has the largest number of aligned reads
                if int(stats[2]) > max_reads:
                    # Store the number of aligned reads
                    max_reads = int(stats[2])
                    # Store chromosome name
                    chromosome = stats[0]

    print chromosome

Save the above code to ``<my_script>.py`` file and mark it executable.

.. code-block:: bash

    # Make the file executable
    chmod +x <my_script>.py

We can now use the uploaded BAM object (``bam``) as input to the
process that we just wrote:

.. code-block:: python

   # Run the custom process on the server
   chr = res.run('max-reads',
                 input={'bam': bam.id},
                 src='/path/to/<process_name>.yaml',
                 tools=['/path/to/<my_script>.py'])

Again, we can inspect the status of the processing step by:

.. code-block:: python

    # Get the latest meta data from the server
    chr.update()

    # Print the status
    chr.status

    # Print the process' standard output
    print(chr.stdout())

We can see the analysis results by inspecting the ``chr`` object's
``output`` fields.

.. code-block:: python

    # Inspect the process output
    chr.output

The name of the chromosome with the most aligned reads is saved in
the ``chr`` output field. The file in the ``stats`` field with the
sequence alignment statistics can be downloaded by:

.. code-block:: python

    # Download chromosome statistics file
    chr.download()

We have covered the basics. Please continue with the
:ref:`introduction` where we explain how the data is organized on the
Resolwe server and how to query existing data sets.

We have shown how to run processes with
the ``run`` command. We define the process to execute on the server
with the slug parameter (*e.g.,* ``alignment-bowtie2``).
The process has to be registered (installed) on the server, or the
command will fail.

.. code-block:: python

   import resdk

   # Sign-in the Resolwe server
   res = resdk.Resolwe('admin', 'admin', 'https://torta.bcm.genialis.com')

   # Get the genome
   genome = res.data.get('hg19')

   # Get a sample
   sample = res.sample.get('human-example-chr22-reads')

   # Access genome ID
   genome_id = genome.id

   # Access the ID of the first data object on the sample
   reads_id = sample.data[0]

   # Run the Bowtie 2 read sequence alignment
   aligned = res.run('alignment-bowtie2',
                     input={
                         'genome': genome_id,
                         'reads': reads_id,
                         'reporting': {'rep_mode': 'k', 'k_reports': 1}
                     })

This is great for running processes, but not so much for development.
Developers want to modify the analysis process. Two arguments of
the ``run`` method help developers with this challenge: ``src`` and
``tools``. With the ``src`` argument, you can reference a local script
that contains process definition. The process definition will first
automatically register (install) on the server and then the data object
would be created and the process would run. The code shows an example.
You can play with the Bowtie2 process locally (in `bowtie.yml`_
file), but the process runs on the server.

.. code-block:: python
   :emphasize-lines: 5

   aligned = res.run('alignment-bowtie2',
                     input={
                         'genome': genome_id,
                         'reads': reads_id,
                         'reporting': {'rep_mode': 'k', 'k_reports': 1}
                     },
                     src='bowtie.yml')

.. _bowtie.yml: https://github.com/genialis/resolwe-bio/blob/master/resolwe_bio/processes/alignment/bowtie.yml

The process's algorithm is written in bash. We can directly call programms that
are included in the runtime (*e.g.,* cat, head and grep). Resolwe
Bioinformatics runs processes in a `Docker container`_ with many
bioinformatics tools pre-installed. In the *Bowtie 2.2.3*
process we call the ``bowtie2`` aligner, ``samtools`` and other
commands.

.. _Docker container: https://github.com/genialis/docker-bio-linux8-resolwe

.. code-block:: bash
   :linenos:
   :lineno-start: 460

   samtools sort "${FW_NAME}_align_unsorted.bam" "${FW_NAME}_align"

Sometimes you may want to write *ad-hoc* scripts and call them from
processes. For instance, to post-process the results of Bowtie, we call
``mergebowtiestats.py``.

.. code-block:: bash
   :linenos:
   :lineno-start: 214

   mergebowtiestats.py $STATS

Resolwe allows to place the *ad-hoc* scripts in a ``tools`` folder that
is added to runtime PATH. The ``tools`` folder is on Resolwe server,
so SDK helps you upload your *ad-hoc* scripts to the server automatically.
Files are transfered via SCP, so you should have an SSH access to the
Resolwe server. Also, you have to configure the `password-less
authentication`_.

.. _password-less authentication: https://docs.fedoraproject.org/en-US/Fedora/14/html/Deployment_Guide/s2-ssh-configuration-keypairs.html

You have to tell the Resolwe SDK where to copy the files. Set the
``TOOLS_REMOTE_HOST`` environment variable in your terminal:

.. code-block:: bash

   export TOOLS_REMOTE_HOST=<username>@torta.bcmt.bcm.edu://genialis/tools

Now you can reference your *ad-hoc* scripts in the ``run`` command with
the tools argument:

.. code-block:: python
   :emphasize-lines: 5

   aligned = res.run('alignment-bowtie2',
                     input={
                         'genome': genome_id,
                         'reads': reads_id,
                         'reporting': {'rep_mode': 'k', 'k_reports': 1}
                     },
                     src='bowtie.yml',
                     tools=['mergebowtiestats.py'])

The tools folder is in the runtime PATH. If you wish to run your
scripts in a Resolwe process, remember to make them executable (*e.g.,*
``chmod +x mergebowtiestats.py``) and set an appropriate shebang_
(*e.g.,* ``#!/usr/bin/env python2`` for Python and
``#!/usr/bin/Rscript`` for R).

.. _shebang: https://en.wikipedia.org/wiki/Shebang_(Unix)

Note that processes are executed asynchronously. This allows you
to write the whole pipeline from start to finish interactivelly in
Python shell, witout waiting for each step to finish. But you have to
manually check if results are ready from time to time:

.. code-block:: python

   # Check the status of your data object
   aligned.update(); aligned.status

You can view the process' ``stdout`` to inspect if it runs as intended
and debug errors:

.. code-block:: python

   # Print the process' standard output
   print(aligned.stdout())

You can read how to write processes in YAML syntax in the
`Writing processes`_ chapter of Resolwe Documentation. You should
review which processes are already available in the `Process catalog`_
and what inputs they accept.

.. _Writing processes: http://resolwe.readthedocs.io/en/latest/proc.html
.. _Process catalog: http://resolwe-bio.readthedocs.io/en/latest/catalog.html
