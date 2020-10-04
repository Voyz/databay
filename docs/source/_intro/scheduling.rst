.. _scheduling:

Scheduling
----------

The principal functionality of Databay is to execute data transfer repeatedly on a pre-defined interval. To facilitate this, links are governed by a scheduler object implementing the :any:`BasePlanner` class. Using the concrete scheduling functionality, links' transfers are executed in respect with their individual interval setting.

To schedule a link, all you need to do is to add it to a planner and call :any:`start <BasePlanner.start>` to begin scheduling.

.. code-block:: python

    link = Link(some_inlet, some_outlet, timedelta(minutes=1))
    planner = SchedulePlanner(link)
    planner.start()

Databay provides two built-in :any:`BasePlanner` implementations based on two popular Python scheduling libraries:

* :any:`ApsPlanner` - using |APS|_.
* :any:`SchedulePlanner` - using Schedule_.

While they differ in the method of scheduling, threading and exception handling, they both cover a reasonable variety of scheduling scenarios. Please refer to their appropriate documentation for more details on the difference between the two.

You can easily use a different scheduling library of your choice by extending the :any:`BasePlanner` class and implementing the link scheduling and unscheduling yourself. See :any:`Extending BasePlanner <extending/extending_base_planner>` for more.

