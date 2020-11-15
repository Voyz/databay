.. _start_shutdown:

Start and shutdown
---------------------

.. rubric::
    Start

To begin scheduling links you need to call :any:`start <BasePlanner.start>` on the planner you're using. Both :any:`ApsPlanner` and :any:`SchedulePlanner` handle :any:`start <BasePlanner.start>` as a synchronous blocking function. To run :any:`start <BasePlanner.start>` without blocking the current thread, wrap its call within a new thread or a process:

.. code-block:: python

    th = Thread(target=planner.start)
    th.start()


.. rubric::
    Shutdown

To stop scheduling links you need to call :any:`shutdown(wait:bool=True) <BasePlanner.shutdown>` on the planner you're using. Note that this may or may not let the currently transferring links finish, depending on the implementation of the :any:`BasePlanner` that you're using. Both :any:`ApsPlanner` and :any:`SchedulePlanner` allow waiting for the links if :any:`shutdown <BasePlanner.shutdown>` is called passing :code:`True` as the :code:`wait` parameter.

.. rubric::
    on_start and on_shutdown

Just before scheduling starts, :any:`Inlet.on_start` and :any:`Outlet.on_start` callbacks will be propagated through all inlets and outlets. Consequently, just after scheduling shuts down, :any:`Inlet.on_shutdown` and :any:`Outlet.on_shutdown` callbacks will be propagated through all inlets and outlets. In both cases, these callbacks will be called only once for each inlet and outlet. Override these callback methods to implement custom starting and shutdown behaviour in your inlets and outlets.

