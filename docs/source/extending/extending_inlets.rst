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

.. container:: tutorial-block

    #. Extend the :any:`Inlet` class, returning produced data from the :any:`pull` method:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../../examples/basic_inlet.py
        :language: python
        :lines: 5-11

    #. Instantiate it:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../../examples/basic_inlet.py
        :language: python
        :lines: 14

    #. Add it to a link and start scheduling:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../../examples/basic_inlet.py
        :language: python
        :lines: 18-25

    Above setup will produce a random integer every 5 seconds (:ref:`See full example <basic-inlet>`).

Each pull call is provided with an :any:`Update` object as a parameter. It contains the name of the governing link (if specified) and an incremental integer index. Use the :code:`str(update)` to get a formatted string of that update. See :any:`Transfer Update <transfer-update>` for more.

Creating records
^^^^^^^^^^^^^^^^

Data produced by inlets is wrapped in :any:`Record` objects before being passed to outlets. If you wish to control how records are created or attach local metadata, use the :any:`Inlet.new_record` method to create records within your inlet and return these instead.

.. code-block:: python

    class RandomIntInlet(Inlet):

        def pull(self, update):
            new_integer = random.randint(0, 100)
            record = self.new_record(payload=new_integer)
            return record

Producing multiple records
^^^^^^^^^^^^^^^^^^^^^^^^^^

During one transfer you may produce multiple data entities within the :any:`Inlet.pull` method. Returning a :any:`list` is an indication that multiple records are being produced at once, in which case each element of the :any:`list` will be turned into a :any:`Record`. Any return type other than :any:`list` (eg. :any:`tuple`, :any:`set`, :any:`dict`) will be considered as one :any:`Record`.

.. rst-class:: mb-s
Returning a :any:`list`, producing two records:

.. rst-class:: highlight-small
.. code-block:: python

    def pull(self, update):

        # produces two records
        return [random.randint(0, 50), random.randint(0, 100)]

.. rst-class:: mb-s
Returning a :any:`set`, producing one record:

.. rst-class:: highlight-small
.. code-block:: python

    def pull(self, update):

        # produces one records
        return {random.randint(0, 50), random.randint(0, 100)}

Same is true when explicitly creating multiple records within :any:`pull` and returning these.

.. code-block:: python

    def pull(self, update):
        first_record = self.new_record(random.randint(0, 50))
        second_record = self.new_record(random.randint(0, 100))

        return [first_record, second_record]

If you wish for one record to contain a :any:`list` of data that doesn't get broken down to multiple records, you can either create the record yourself passing the :any:`list` as payload or return a nested :any:`list`:

.. code-block:: python

    def pull(self, update):
        r1 = random.randint(0, 50)
        r2 = random.randint(0, 100)

        return self.new_record(payload=[r1, r2])

    # or
    ...

    def pull(self, update):
        r1 = random.randint(0, 50)
        r2 = random.randint(0, 100)

        return [[r1, r2]]

.. _global_metadata:

Global metadata
^^^^^^^^^^^^^^^

:any:`Inlet` can attach custom metadata to all records it produces. Metadata's intended use is to provide additional context to records when they are consumed by outlets. To do so, when constructing an :any:`Inlet` pass a metadata dictionary, a copy of which will be attached to all records produced by that :any:`Inlet` instance.

.. code-block:: python

    random_cat_inlet = RandomIntInlet(metadata={'animal': 'cat'})
    # produces Record(metadata={'animal': 'cat'})

    random_parrot_inlet = RandomIntInlet(metadata={'animal': 'parrot'})
    # produces Record(metadata={'animal': 'parrot'})

Metadata dictionary is independent from the inlet that it is given to. Inlet should not modify the metadata or read it; instead inlets should expect all setup parameters to be provided as arguments on construction.

.. rst-class:: mb-s
Incorrect:

.. rst-class::highlight-small
.. code-block:: python

    def MyInlet():
        def __init__(self, metadata):
            self.should_do_stuff = metadata.get('should_do_stuff')

.. rst-class:: mb-s
Correct:

.. rst-class::highlight-small
.. code-block:: python

    def MyInlet():
        def __init__(self, should_do_stuff, *args, **kwargs):
            super().__init__(*args, **kwargs) # metadata dict gets passed and stored here
            self.should_do_stuff = should_do_stuff

Metadata supported by each outlet differs and is dependant on the particular outlet implementation. Please refer to specific outlet documentation for more information on metadata expected.


Additionally, each record is supplied with a special :code:`__inlet__` metadata entry containing string representation of the inlet that produced it.

.. code-block:: python

    >>> record.metadata['__inlet__']
    RandomIntInlet(metadata={})



Local metadata
^^^^^^^^^^^^^^

Apart providing an inlet with :ref:`global_metadata` that will be same for all records, you may also attach local per-record metadata that can vary for each record. This can be done inside of the :any:`pull` method by specifying a metadata dictionary when creating a record using :any:`Inlet.new_record` method.


.. code-block:: python

    class RandomIntInlet(Inlet):

        def pull(self, update):
            new_integer = random.randint(0, 100)

            if new_integer > 50:
                animal = 'cat'
            else:
                animal = 'parrot'

            record = self.new_record(payload=new_integer, metadata={'animal': animal})
            return record

Note that local metadata will override global metadata if same metadata is specified globally and locally.





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
