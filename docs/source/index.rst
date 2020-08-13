.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. |Asyncio| replace:: **Asyncio**

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
* :ref:`Examples <examples>` - See Databay in use.
* :any:`Extending Databay <extending>` - Use Databay in your project.
* :any:`API Reference <api/databay/index>` - Read the API documentation.


Features
--------


.. list-table::

    *   - **Simple, decoupled interface**
        - Easily implement :ref:`data production <extending_inlets>` and :ref:`consumption <extending_outlets>` that fits your needs.

    *   - **Granular control over data transfer**
        -  Multiple ways of :ref:`passing information <records>` between producers and consumers.

    *   - |Asyncio|_ **supported**
        - You can :ref:`produce <async_inlet>` or :ref:`consume <async_outlet>` asynchronously.

    *   - **We'll handle the rest**
        - :ref:`scheduling`, :ref:`startup and shutdown <start_shutdown>`, :ref:`exception handling <exception_handling>`, :ref:`logging <logging>`.

    *   - **Support for custom scheduling**
        - Use :ref:`your own scheduling logic <extending_base_planner>` if you like.

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
    planner = APSPlanner(link)
    planner.start()

Every 5 seconds this snippet will pull data from a test URL, and write it to MongoDB.

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