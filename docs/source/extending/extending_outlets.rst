.. _extending_outlets:

Extending Outlets
=================

.. contents::
    :local:
    :backlinks: entry

To implement custom data consumption you need to extend the :any:`Outlet` class and override the :any:`Outlet.push` method.

Simple example
^^^^^^^^^^^^^^

.. code-block:: python

    from databay import Outlet

    class PrintOutlet(Outlet):

        def push(self, records, update):
            print(records)

Such outlet is ready to be added to a link and used in Databay.

.. code-block:: python

    from databay import Link
    from databay.planners import APSPlanner
    from datetime import timedelta

    print_outlet = PrintOutlet()
    link = Link([...some inlets...], print_outlet, interval=timedelta(seconds=5))

    planner = APSPlanner()
    planner.add_link(link)
    planner.start()

Above setup will print all records transferred by that link (:ref:`See full example <basic-outlet>`).

Each push call is provided with an :any:`Update` object as one of parameters. It contains the name of the governing link (if specified) and an incremental integer index. Use the :code:`str(update)` to get a formatted string of that update.

Consuming Records
^^^^^^^^^^^^^^^^^

Outlets are provided with a list of all records produced by all inlets of the governing link. Each :any:`Record` contains two fields:

1. :any:`Record.payload` - data stored in the record.
2. :any:`Record.metadata` - metadata attached to the record

.. code-block:: python

    from databay import Outlet

    class ConditionalPrintOutlet(Outlet):

        def push(self, records, update):
            for record in records:
                if 'should_print' in record.metadata and record.metadata['should_print'] == True:
                    print(f'Record data: {record.payload} with metadata: {record.metadata}')

By default a copy of records is provided to outlets in order to prevent accidental data corruption. You can disable this mechanism by passing :code:`copy_records=False` when constructing a link, in which case same list will be provided to all outlets. Ensure you aren't modifying the records or their underlying data in your :any:`Outlet.push` method.

Metadata
^^^^^^^^

Your outlet can be built to behave differently depending on the metadata carried by the records. Metadata is attached to each record when inlets produce data. When creating an outlet it is up to you to ensure the expected metadata and its effects are clearly documented.

To prevent name clashes between various outlets' metadata, it is recommended to implement non-string keys expected by your outlet.

.. code-block:: python

    class CsvOutlet(Outlet):
        CSV_FILE = object()

        def push(self, records:[Record], update):
            for record in records:
                if self.CSV_FILE in record.metadata:
                    csv_file = record.metadata[self.CSV_FILE]
                else:
                    csv_file = 'default.csv'

                ...
                # write to csv_file specified


    ...

    random_int_inletA = RandomIntInlet(metadata={CsvOutlet.CSV_FILE: 'cat.csv'})
    random_int_inletB = RandomIntInlet(metadata={CsvOutlet.CSV_FILE: 'dog.csv'})

Start and shutdown
^^^^^^^^^^^^^^^^^^

All outlets contain :any:`Outlet.active` flag that is set by the governing link when scheduling starts and unset when scheduling stops. You can use this flag to refine the behaviour of your outlet.

You can further control the starting and shutting down functionality by overriding the :any:`Outlet.on_start` and :any:`Outlet.on_shutdown` methods. If one :any:`Outlet` instance is governed by multiple links, these callbacks will be called only once per instance by whichever link executes first.

.. code-block:: python

    class PrintOutlet(Outlet):

        def push(self, records, update):
            print(f'{self.prefix} - {records}')

        def on_start(self):
            self.prefix = 'foo'

Asynchronous outlet
^^^^^^^^^^^^^^^^^^

You may implement asynchronous data consumption by defining :any:`Outlet.push` as a coroutine.

.. code-block:: python

    import asyncio
    from databay import Outlet

    class AsyncOutlet(Outlet):

        # Note the 'async' keyword
        async def push(self, records, update):
            async_results = await some_async_code(records)
            await asyncio.sleep(1)

----

.. rubric:: Next Steps

#. Learn about extending :ref:`Inlets <extending_inlets>`.
#. See the :any:`Examples <../examples>`