.. _exception_handling:

Exception handling
------------------

If an exception is thrown during transfer, both planners can be set to catch these by passing the :code:`ignore_exceptions=True` parameter on construction. This ensures transfer of remaining links can carry on even if some links are erroneous. If exceptions aren't caught, both :any:`ApsPlanner` and :any:`SchedulePlanner` will log the exception and shutdown.

Additionally, each :any:`Link` can be configured to catch exceptions by passing :code:`ignore_exceptions=True` on construction. This way any exceptions raised by individual inlets and outlets can be logged and ignored, allowing the remaining nodes to continue execution and for the transfer to complete.

.. code-block:: python

    # for planners
    planner = SchedulePlanner(ignore_exceptions=True)
    planner = ApsPlanner(ignore_exceptions=True)

    # for links
    link = Link(..., ignore_exceptions=True)