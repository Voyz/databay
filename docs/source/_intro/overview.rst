.. _overview:

Overview
--------

.. container:: text-block

    Databay is a Python interface for scheduled data transfer.

    It facilitates transfer of (any) data from A to B, on a scheduled interval.

In Databay, data transfer is expressed with three components:

* :any:`Inlets <Inlet>` - for data production.
* :any:`Outlets <Outlet>` - for data consumption.
* :any:`Links <Link>` - for handling the data transit between inlets and outlets.

Scheduling is implemented using third party libraries, exposed through the :any:`BasePlanner` interface. Currently two BasePlanner implementations are available - using |APS|_ (:any:`APSPlanner`) and Schedule_ (:any:`SchedulePlanner`).

:ref:`A simple example <simple-usage>`:

.. code-block:: python

    # Create an inlet, outlet and a link.
    http_inlet = HttpInlet('https://some.test.url.com/')
    mongo_outlet = MongoOutlet('databay', 'test_collection')
    link = Link(http_inlet, mongo_outlet, datetime.timedelta(seconds=5))

    # Create a planner, add the link and start scheduling.
    planner = APSPlanner(link)
    planner.start()

Every 5 seconds this snippet will pull data from a test URL, and write it to a MongoDB.

While Databay comes with a handful of built-in inlets and outlets, its strength lies in extendability. To use Databay in your project, create concrete implementations of :any:`Inlet` and :any:`Outlet` classes that handle the data production and consumption functionality you require. Databay will then make sure data can repeatedly flow between the inlets and outlets you create. :ref:`Extending Inlets <extending_inlets>` and :ref:`extending Outlets <extending_outlets>` is easy and has a wide range of customization. Head over to :any:`Extending Databay <extending>` section for a detailed explanation.