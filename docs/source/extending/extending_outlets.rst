.. _extending_outlets:

Extending Outlets
=================

.. contents::
    :local:
    :backlinks: entry

To implement custom data consumption you need to extend the :any:`Outlet` class and override the :any:`Outlet.push` method.

Simple example
--------------

.. container:: tutorial-block

    #. Extend the :any:`Outlet` class, printing the incoming data in the :any:`push <Outlet.push>` method:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../../examples/basic_outlet.py
        :language: python
        :start-at: class PrintOutlet
        :end-at: print(update,

    #. Instantiate it:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../../examples/basic_outlet.py
        :language: python
        :start-at: print_outlet = PrintOutlet
        :end-at: print_outlet = PrintOutlet

    #. Add it to a link and and schedule:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../../examples/basic_outlet.py
        :language: python
        :start-at: link = Link(
        :end-at: planner.start

    Above setup will print all records transferred by that link (:ref:`See full example <basic-outlet>`).

Each push call is provided with an :any:`Update` object as one of parameters. It contains the tags of the governing link (if specified) and an incremental integer index. Use the :code:`str(update)` to get a formatted string of that update. See :any:`Transfer Update <transfer-update>` for more.

Consuming Records
-----------------


Outlets are provided with a :any:`list` of all records produced by all inlets of the governing link. Each :any:`Record` contains two fields:

1. :any:`Record.payload` - data stored in the record.
2. :any:`Record.metadata` - metadata attached to the record

.. code-block:: python

    from databay import Outlet

    class ConditionalPrintOutlet(Outlet):

        def push(self, records, update):
            for record in records:
                if record.metadata.get('should_print', False):
                    print(record.payload)

By default a copy of records is provided to outlets in order to prevent accidental data corruption. You can disable this mechanism by passing :code:`copy_records=False` when constructing a link, in which case the same :any:`list` will be provided to all outlets. Ensure you aren't modifying the records or their underlying data in your :any:`Outlet.push` method.

Metadata
--------

Your outlet can be built to behave differently depending on the metadata carried by the records. Metadata is attached to each record when inlets produce data. Learn more about the difference between :ref:`Global metadata <global_metadata>` and :ref:`Local metadata <local_metadata>`.

When creating an outlet it is up to you to ensure the expected metadata and its effects are clearly documented. To prevent name clashes between various outlets' metadata, it is recommended to include outlet name in the metadata keys expected by your outlet.

.. rst-class:: mb-s

    Incorrect:

.. rst-class:: highlight-small
.. code-block:: python

    CSV_FILE = 'CSV_FILE'

.. rst-class:: mb-s

    Correct:

.. rst-class:: highlight-small
.. code-block:: python

    CSV_FILE = 'CsvOutlet.CSV_FILE'

.. code-block:: python

    class CsvOutlet(Outlet):

        # Name of csv file to write records to.
        CSV_FILE = 'CsvOutlet.CSV_FILE'

        def push(self, records:[Record], update):
            for record in records:
                if self.CSV_FILE in record.metadata:
                    csv_file = record.metadata[self.CSV_FILE] + '.csv'

                    ...
                    # write to csv_file specified

    ...

    random_int_inletA = RandomIntInlet(metadata={CsvOutlet.CSV_FILE: 'cat'})
    random_int_inletB = RandomIntInlet(metadata={CsvOutlet.CSV_FILE: 'dog'})

.. image:: ../_static/images/databay_metadata_csv.png

For clarity and readability, Databay provides the :any:`MetadataKey` type for specifying metadata key class attributes.

.. rst-class:: highlight-small
.. code-block:: python

    from databay.outlet import MetadataKey

    class CsvOutlet(Outlet):
        CSV_FILE:MetadataKey = 'CsvOutlet.CSV_FILE'

Start and shutdown
------------------

All outlets contain :any:`Outlet.active` flag that is set by the governing link when scheduling starts and unset when scheduling stops. You can use this flag to refine the behaviour of your outlet.

You can further control the starting and shutting down functionality by overriding the :any:`Outlet.on_start` and :any:`Outlet.on_shutdown` methods. If one :any:`Outlet` instance is governed by multiple links, these callbacks will be called only once per instance by whichever link executes first.

.. code-block:: python

    class PrintOutlet(Outlet):

        def push(self, records, update):
            print(f'{self.prefix} - {records}')

        def on_start(self):
            self.prefix = 'foo'

.. _async_outlet:

Asynchronous outlet
-------------------

You may implement asynchronous data consumption by defining :any:`Outlet.push` as a coroutine.

.. code-block:: python

    import asyncio
    from databay import Outlet

    class AsyncOutlet(Outlet):

        # Note the 'async' keyword
        async def push(self, records, update):
            async_results = await some_async_code(records)
            await asyncio.sleep(1)

See :ref:`Basic Asynchronous <basic-asynchronous>` for a full example of implementing asynchronous code in Databay.

----

.. rubric:: Next Steps

#. Learn about extending :ref:`Inlets <extending_inlets>`.
#. See the :any:`Examples <../examples>`