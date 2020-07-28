.. _async_keyword: https://docs.python.org/3/library/asyncio-task.html#coroutines

.. _extending_inlets:

Extending Inlets
================

.. contents::
    :local:
    :backlinks: entry

To implement custom data production you need to extend the :any:`Inlet` class, override the :any:`Inlet.pull` method and return the data produced.

Simple example
^^^^^^^^^^^^^^

.. code-block:: python

    import random
    from databay import Inlet

    class RandomIntInlet(Inlet):

        def pull(self, update):
            return random.randint(0, 100)

Such inlet is ready to be added to a link and used in Databay.

.. code-block:: python

    from databay import Link
    from databay.planners import APSPlanner
    from datetime import timedelta

    random_int_inlet = RandomIntInlet()
    link = Link(random_int_inlet, [...some outlets...], interval=timedelta(seconds=5))

    planner = APSPlanner()
    planner.add_link(link)
    planner.start()

Above setup will produce a random integer every 5 seconds (:ref:`See full example <basic-inlet>`).

Each pull call is provided with an :any:`Update` object as a parameter. It contains the name of the governing link (if specified) and an incremental integer index. Use the :code:`str(update)` to get a formatted string of that update.

Creating records
^^^^^^^^^^^^^^^^

Data produced by inlets is wrapped in :any:`Record` objects before being passed to outlets. If you wish to control how records are created or attach local metadata, use the :any:`Inlet.new_record` method to create records within your inlet and return these instead.

.. code-block:: python

    class RandomIntInlet(Inlet):

        def pull(self, update):
            new_integer = random.randint(0, 100)
            record = self.new_record(payload=new_integer)
            return record


.. _global_metadata:

Global metadata
^^^^^^^^^^^^^^^

Inlets can attach metadata to records that can later be used by outlets. When constructing an :any:`Inlet` instance you can provide a metadata dictionary, a copy of which will be attached to all records produced by that :any:`Inlet` instance.

.. code-block:: python

    random_cat_inlet = RandomIntInlet(metadata={'type': 'cat'})
    # produces Record(metadata={'type': 'cat'})

    random_parrot_inlet = RandomIntInlet(metadata={'type': 'parrot'})
    # produces Record(metadata={'type': 'parrot'})

Additionally, each record is supplied with a special :code:`__inlet__` metadata entry containing string representation of the inlet that produced it.

.. code-block:: python

    >>> record.metadata['__inlet__']
    RandomIntInlet(metadata={})

The metadata required by each outlet differs and is dependant on the particular outlet implementation. Please refer to specific outlet documentation for more information on metadata supported.

Local metadata
^^^^^^^^^^^^^^

Apart from specifying :ref:`global_metadata`, you may also attach local per-record metadata. This can be done by providing a metadata dictionary when creating a record using :any:`Inlet.new_record` method.

Note that local metadata will override global metadata if same metadata is specified globally and locally.

.. code-block:: python

    class RandomIntInlet(Inlet):

        def pull(self, update):
            new_integer = random.randint(0, 100)
            record = self.new_record(payload=new_integer, metadata={'random_cap': 100})
            return record



Producing multiple records
^^^^^^^^^^^^^^^^^^^^^^^^^^

On each transfer you may return single or multiple data entities from the :any:`Inlet.pull` method.

.. code-block:: python

    class TwoRandomIntsInlet(Inlet):

        def pull(self, update):
            return [random.randint(0, 50), random.randint(0, 100)]

Same is true when explicitly producing multiple records.

.. code-block:: python

    class TwoRandomIntsInlet(Inlet):

        def pull(self, update):
            first_new_integer = random.randint(0, 50)
            second_new_integer = random.randint(0, 100)

            first_record = self.new_record(payload=first_new_integer, metadata={'random_cap': 50})
            second_record = self.new_record(payload=second_new_integer, metadata={'random_cap': 100})
            return [first_record, second_record]


Start and shutdown
^^^^^^^^^^^^^^^^^^

All inlets contain :any:`Inlet.active` flag that is set by the governing link when scheduling starts and unset when scheduling stops. You can use this flag to refine the behaviour of your inlet.

You can further control the starting and shutting down functionality by overriding the :any:`Inlet.on_start` and :any:`Inlet.on_shutdown` methods. If one :any:`Inlet` instance is governed by multiple links, these callbacks will be called only once per instance by whichever link executes first.

.. code-block:: python

    class RandomIntInlet(Inlet):

        def pull(self, update):
            return random.randint(0, 100)

        def on_start(self):
            random.seed(42)

Asynchronous inlet
^^^^^^^^^^^^^^^^^^

You may implement asynchronous data production by defining :any:`Inlet.pull` as a coroutine. The governing link will await all its inlets to finish producing their data before passing the results to outlets.

.. code-block:: python

    import asyncio
    from databay import Inlet

    class AsyncInlet(Inlet):

        # Note the 'async' keyword
        async def pull(self, update):
            async_results = await some_async_code()
            await asyncio.sleep(1)
            return async_results

Test your inlet
^^^^^^^^^^^^^^^

Databay comes with a template :any:`unittest.TestCase` designed to validate your implementation of :any:`Inlet` class. To use it, create a new test class extending :any:`InletTester` and implement :any:`InletTester.get_inlet` method returning an instance of your inlet.

.. code-block:: python

    from databay.misc import inlet_tester

    class RandomIntInletTest(inlet_tester.InletTester):

        def get_inlet(self, metadata):
            return RandomIntInlet(metadata=metadata)

        ...

        # You can add further tests here

Running such concrete test will execute a variety of test cases that ensure your inlet correctly provides the expected functionality. These include:

* Creating new records.
* Attaching global and local metadata.
* Calling :any:`pull` method.

Since :any:`InletTester` will call pull on your inlet, you may want to mock some functionality of your inlet in order to separate testing of your inlet logic from external code.

----

.. rubric:: Next Steps

#. Learn about extending :ref:`Outlets <extending_outlets>`.
#. See the :any:`Examples <../examples>`
