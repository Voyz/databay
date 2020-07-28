Databay
==============

`Databay on GitHub <https://github.com/Voyz/databay>`_
------------------------------------------------------

..
    .. autosummary::
        :toctree: _autosummary
        :recursive:

        databay


Databay is a Python interface for scheduled data transfer.

Its primary purpose is to facilitate transfer of (any) data from A to B, on a scheduled interval. Read more about :any:`key concepts <introduction>` of Databay or see the :any:`examples <examples>` to get started.

.. code-block:: python

    # Create an inlet, outlet and a link.
    http_inlet = HttpInlet('https://some.test.url.com/')
    mongo_outlet = MongoOutlet('databay', 'test_collection')
    link = Link(http_inlet, mongo_outlet, datetime.timedelta(seconds=5))

    # Create a planner, add the link and start scheduling.
    planner = APSPlanner()
    planner.add_link(link)
    planner.start()

Every 5 seconds this snippet will pull data from a test URL, and write it to a MongoDB.

.. toctree::
   :maxdepth: 1

   introduction
   extending
   scheduling
   examples
   api/databay/index
   _modules/index