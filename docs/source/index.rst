

Databay
=======

.. container:: text-block

    Databay is a Python interface for **scheduled data transfer**.

    It facilitates transfer of (any) data from A to B, on a scheduled interval.


`GitHub Page <https://github.com/Voyz/databay>`_
------------------------------------------------

..
    .. autosummary::
        :toctree: _autosummary
        :recursive:

        databay

.. code-block:: python

    pip install databay


* :ref:`Overview <overview>` - Learn what is Databay.
* :any:`Examples <examples>` - See Databay in use.
* :any:`Extending Databay <extending>` - Use Databay in your project.
* :any:`API Reference <api/databay/index>` - Read the API documentation.


.. rst-class:: mb-s
:ref:`A simple example <simple-usage>`:

.. code-block:: python


    # Data producer
    inlet = HttpInlet('https://some.test.url.com/')

    # Data consumer
    outlet = MongoOutlet('databay', 'test_collection')

    # Data transfer between the two
    link = Link(inlet, outlet, datetime.timedelta(seconds=5))

    # Start scheduling
    planner = APSPlanner()
    planner.add_link(link)
    planner.start()

Every 5 seconds this snippet will pull data from a test URL, and write it to a MongoDB.

----

.. rubric:: Explore this documentation:

.. toctree::
    :maxdepth: 1

    introduction
    extending
    examples
    api/databay/index
    _modules/index
    GitHub Page <https://github.com/Voyz/databay>


.. todo: add filters
.. todo: add translators