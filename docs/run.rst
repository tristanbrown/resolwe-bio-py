=============================
Upload data and run pipelines
=============================

So far we were only inspecting data: accessing information and
downloading files. Here we explain how to upload new data and run
data analytics pipelines.

The obvious way to start the analysis is to upload some data to Resolwe.
We will do that by using process of type upload. It may sound strange at
first, but uploading the data to Resolwe is exactly the same as running
any other process. We have inputs - path to some file on our local
computer, an algorithm (some file transfer protocol) and output -
reference to a file freshly uploaded on Resolwe server.

There are many upload processes, since there are many different types
of files that can be uploaded. How to find all possible upload
processes? Well, using the knowledge from previous chapter:

.. literalinclude:: files/resdk-example.py
   :lines: 63

Method run
==========

Uploading file to Resolwe is as easy as:

.. literalinclude:: files/resdk-example.py
   :lines: 65-66

As you can see, we have provided just process ``slug`` and ``input``
parameters. What the method returns is a data object (in our case,
called ``reads``). After uploading reads, we may want to assemble
them with *Abyss*:

.. literalinclude:: files/resdk-example.py
   :lines: 68-69

Here you see how to include a data object that is already uploaded on
Resolwe - with it's id.

You probably noticed that we get the result almost instantly, while
typical assembling process can last multiple hours. This is because all
processing runs asynchronously, so the returned data object does not
have an OK status or outputs when returned. Use
``assembled_reads.update()`` to refresh the information. Also, to
estimate remaining time ``assembled_reads.process_progress`` can be
useful.

From the documentation of method :any:`run <Resolwe.run>` we see how
to run process in general::

    result = res.run(slug=None,
                     input={},
                     descriptor=None,
                     descriptor_schema=None,
                     collections=[],
                     data_name='',
                     src=None,
                     tools=None)

Each of the parameters will be described in it own sub-section

Slug
----

The first agrument is the slug of process to use. You can find process
slug by using methods ``get()`` end ``filter()`` browsing the process
endpoint.

Input
-----

As seen in the upper example, inputs are given with dictionary of
``"input_name":input_value`` key-value pairs. But how to know what are
all the possible inputs for a given process? Well, this is excactly
what input schema is for - it defines the names and types of inputs
for given process:

.. literalinclude:: files/resdk-example.py
   :lines: 71

The output may not be most visually intuitive so this image may help
to recognize the structure:

.. figure:: images/input_schema.jpg
   :width: 60 %

   Each ``input_schema`` is a *list* of *dictionaries* - in this case
   there are 5 of them. Each dictionary contains three mandatory keys:
   ``name``, ``label`` and ``type``. As you will notice there are also
   some optional fields. This holds true for all dictionaries in
   ``input_schema``, except for the ones containing the ``group`` key.
   As the names suggests, this is just a way to pack a group of inputs
   together, one level lower in hierarchy. Typically these are
   flags/parameters for the command line programs used in process's
   algorithm.

A handy function when inspectig process inputs is ``print_inputs()``:

.. literalinclude:: files/resdk-example.py
   :lines: 73

The output tries to give a quick reference in the form of
``- name [type] - label``. Each input corresponds to one line and
``group`` inputs are indented to make a clear separation from the top
level inputs.

Descriptor schema and descriptor
--------------------------------

When creating data object (uploading reads, for example), you can
optionally provide a ``descriptor_schema`` and a ``descriptor``.
Descriptor_schema is just a schema - similar to input_schema or
output_schema. It defines how the descriptor should look like. If you
provide these two, Resolwe will create a *sample* with the annotation
defined in descriptor. It will also include the created data object
(uploaded reads) in the sample. Additionally, all data objects derived
from reads, will be also automatically included in the same sample.
in this way, organization of data objects is handled automatically.

Collections
-----------

If you would like to include the data object in a certain collection,
this is the place to do it. Provide a list of collection id's and the
data object will be included in all of them.

Data name
---------

Process defines what will be the name of it's outputs by itself.
However, if you would like to manually set the name of created data
object, provide it with the ``data_name`` parameter.

Src and tools
-------------

These are used only when developing your own processes. To know more
about that, continue on :doc:`writing pipelines. </pipelines>`

-----------------------------------------------------------------------

Now that we know how the handle all the parameters, lets create a
data object with ful set of parameters:

.. literalinclude:: files/resdk-example.py
   :lines: 75-93

What was just done?

* A data object which will use process ``assembler-abyss`` was created.
* Process will use single-end reads from data object ``reads``, the name of the assembler output files will be ``blah_blah`` and the assembler will use the flags ``k`` and ``n`` with values 20 and 30 respectively.
* We provided the descriptor schema and descriptor with some basic sample information.
* Data object will be included in collections 1 and 2.
* Data object name was set to "my_favourite_name".

Solving problems
================

Sometimes the data object will not have an "OK" status. In such case,
it is helpful to be able to check what went wrong (and where).
Method :any:`stdout <resdk.resources.Data.stdout>` for data objects
can be really helpful in such cases - it saves the standard output of
data object's algorithm and returns it as a string:

.. literalinclude:: files/resdk-example.py
   :lines: 96-99

Also, inpecting info, warning and error logs can be useful:

.. literalinclude:: files/resdk-example.py
   :lines: 101-103

-----------------------------------------------------------------------

This should get you started, but for more info regarding Resolwe in
general, visit `Resolwe documentation.`_

.. _`Resolwe documentation.`: http://resolwe.readthedocs.io/en/latest/

