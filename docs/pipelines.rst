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

Here we have explicitly specified which process to execute on the server,
with the process slug parameter (*i.e.* alignment-bowtie-2-2-3_trim).
The process has to be registered (installed) in the server, or the
command would fail.

This is great for running pipelines, but not so much for development.
Developers want to modify the server process itself. Two argument of
the ``run`` method help developers overcome this challenge, ``src`` and
``tools``. With the ``src`` argument, you can reference a local script
with process definition. The process definition will first be registered
on the server and then algorithm would run. This code would allow you
to play with the Bowtie2 process locally (in the `bowtie.yml`_ file):

.. code-block:: python

   genome = re.data.get('hg19')
   reads = re.data.get('TODO: Slug')
   aligned = re.run('alignment-bowtie-2-2-3_trim', input={
                        genome: genome.id,
                        reads: reads.id,
                        reporting: {rep_mode: 'k', k_reports: 1}
                    }, src='bowtie.yml')

.. _bowtie.yml: https://github.com/genialis/resolwe-bio/blob/master/resolwe_bio/processes/alignment/bowtie.yml

TODO: Write about the tools argument.
