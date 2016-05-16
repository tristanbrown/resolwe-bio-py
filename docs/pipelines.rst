=================
Writing pipelines
=================

Resolwe SDK supports running processes on the Resolwe server with the
run command:

.. code-block:: python

   genome = re.data.get('hg19')
   reads = re.data.get('TODO: Slug')
   aligned = re.run('alignment-bowtie-2-2-3_trim', input={
                        genome: genome.id,
                        reads: reads.id,
                        reporting: {rep_mode: 'k', k_reports: 1}
                    })

Here we explicitly specify which process to execute on the server,
with the process slug parameter (*i.e.* alignment-bowtie-2-2-3_trim).
The process has to be registered (installed) in the server, or the
command would fail.

This is great for running processes, but not so much for development.
Developers want to modify the analysis process itself. Two argument of
the ``run`` method help developers overcome this challenge, ``src`` and
``tools``. With the ``src`` argument, you can reference a local script
with process definition. The process definition will first
automatically register (install) on the server and then the algorithm
would run. The code below allows just that. You can play with the
Bowtie2 process locally (in the `bowtie.yml`_ file), but the process
runs on the server:

.. code-block:: python
   :emphasize-lines: 7

   genome = re.data.get('hg19')
   reads = re.data.get('TODO: Slug')
   aligned = re.run('alignment-bowtie-2-2-3_trim', input={
                        genome: genome.id,
                        reads: reads.id,
                        reporting: {rep_mode: 'k', k_reports: 1}
                    }, src='bowtie.yml')

.. _bowtie.yml: https://github.com/genialis/resolwe-bio/blob/master/resolwe_bio/processes/alignment/bowtie.yml

The processes are written in bash. We can directly call programms that
are included in the runtime (*e.g.,* cat, head and grep). Resolwe
Bioinformatics runs processes in a `Docker container`_ with many
bioinformatics tools pre-installed. In the *Aligner (Bowtie 2.2.3)*
process we call the ``bowtie2`` aligner, ``samtools`` and other
commands.

.. _Docker container: https://github.com/genialis/docker-bio-linux8-resolwe

.. code-block:: bash
   :linenos:
   :lineno-start: 517

   samtools sort "${NAME}_align_unsorted.bam" "${NAME}_align"

Sometime you wish to write ad-hoc scripts and call them from processes.
For instance, to post-process Bowtie results, we call
``mergebowtiestats.py``.

.. code-block:: bash
   :linenos:
   :lineno-start: 247

   mergebowtiestats.py $STATS

Resolwe allows to place the ad-hoc scripts in a ``tools`` folder that
is added to runtime PATH. The ``tools`` folder is on Resolwe server,
so SDK helps you upload your ad-hoc scripts to the server automatically.
Files are transfares via SCP, so you should have an SSH access to the
Resolwe server. Also, you have to configure the `password-less
authentication`_.

.. _password-less authentication: https://docs.fedoraproject.org/en-US/Fedora/14/html/Deployment_Guide/s2-ssh-configuration-keypairs.html

You have to tell the Resolwe SDK where to copy the files. Set the
``TOOLS_REMOTE_HOST`` envronment variable in your terminal:

.. code-block:: bash

   export TOOLS_REMOTE_HOST=<username>@torta.bcmt.bcm.edu://genialis/tools

Now you can reference your ad-hoc scripts in the ``run`` command with
the tools argument:

.. code-block:: python
   :emphasize-lines: 7

   genome = re.data.get('hg19')
   reads = re.data.get('TODO: Slug')
   aligned = re.run('alignment-bowtie-2-2-3_trim', input={
                        genome: genome.id,
                        reads: reads.id,
                        reporting: {rep_mode: 'k', k_reports: 1}
                    }, src='bowtie.yml', tools=['mergebowtiestats.py'])

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

   aligned.update()
   print aligned.status

You can view the process' ``stdout`` to inspect if it runs as intended
and debug errors:

.. code-block:: python

   aligned.stdout()


You can read how to write processes in YAML syntax in the
`Writing processes`_ chapter of Resolwe Documentation. You should
review which processes are already available in Resolwe Bioinformatics
and what inputs they accept. This information is not yet included in
`Resolwe Bio Documentation`_, but you can explore the
`Resolwe Bio processes' source code`_.

.. _Writing processes: http://resolwe.readthedocs.io/en/latest/proc.html
.. _Resolwe Bio Documentation: http://resolwe-bio.readthedocs.io
.. _Resolwe Bio processes' source code: https://github.com/genialis/resolwe-bio/tree/master/resolwe_bio/processes
