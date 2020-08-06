.. _extending_base_planner:

Extending BasePlanner
=====================

Databay comes with two implementations of BasePlanner - :any:`APSPlanner` and :any:`SchedulePlanner`. If you require custom scheduling functionality outside of these two interfaces, you can create your own implementation of :any:`BasePlanner`. Have a look at the two existing implementations for reference: `APSPlanner <../_modules/databay/planners/aps_planner.html>`_ and `SchedulePlanner <../_modules/databay/planners/schedule_planner.html>`_.

To extend the :any:`BasePlanner` you need to provide a way of executing :any:`Link.transfer` method repeatedly by implementing the following four methods. Note that all of these methods are private since they are called internally by BasePlanner and should not be executed directly.

.. container:: contents local topic

    * `_schedule <extending_base_planner.html#schedule>`__
    * `_unschedule <extending_base_planner.html#unschedule>`__
    * `_start_planner <extending_base_planner.html#start-planner>`__
    * `_shutdown_planner <extending_base_planner.html#shutdown-planner>`__


_schedule
^^^^^^^^^

Schedule a :any:`Link`. This method runs whenever :any:`add_links` is called and should not be executed directly. It should accept a link and add the :any:`Link.transfer` method to the scheduling system you're using. Note that you do not need to store the link in your planner - BasePlanner will automatically store it under :any:`BasePlanner.links` when :any:`add_links` is called. It isn't required for the scheduling to be already running when :code:`_schedule` is called.

Each link comes with a :any:`datetime.timedelta` interval providing the frequency at which its :any:`Link.transfer` method should be run. Use :any:`Link.interval` and schedule according to the interval specified.

If the scheduler you're using utilises some form of task-managing job objects, you must assign these to the link being scheduled using :any:`Link.set_job`. This is to ensure the job can be correctly destroyed later when :any:`remove_links <BasePlanner.remove_links>` is called.

Example from :any:`APSPlanner._schedule`:

.. code-block:: python

    def _schedule(self, link:Link):
        job = self._scheduler.add_job(link.transfer,
            trigger=IntervalTrigger(seconds=link.interval.total_seconds()))

        link.set_job(job)



_unschedule
^^^^^^^^^^^

Unschedule a :any:`Link`. This method runs whenever :any:`remove_links` is called and should not be executed directly. It should accept a link and remove it from the scheduling system you're using. Note that you do not need to remove the link from your planner - BasePlanner will automatically remove that link from :any:`BasePlanner.links` when :any:`remove_links` is called. It isn't required for the scheduling to be already stopped when :code:`_unschedule` is called.

If the scheduler you're using utilises some form of task-managing job objects, you may access these using :any:`Link.job` in order to correctly destroy them if necessary when :any:`_unschedule` is called.

Example from :any:`APSPlanner._unschedule`:

.. code-block:: python

    def _unschedule(self, link:Link):
        if link.job is not None:
            link.job.remove()
            link.set_job(None)

_start_planner
^^^^^^^^^^^^^^

Start the scheduling. This method runs whenever :any:`start` is called and should not be executed directly. It should begin the scheduling of links.

This method will be called just after all :any:`Inlet.on_start` and :any:`Outlet.on_start` are called.

Example from :any:`APSPlanner._start_planner`:

.. code-block:: python

    def _start_planner(self):
        self._scheduler.start()

_shutdown_planner
^^^^^^^^^^^^^^^^^

Shutdown the scheduling. This method runs whenever :any:`shutdown` is called and should not be executed directly. It should shutdown the scheduling of links.

A :code:`wait` parameter is provided that you can pass down to your scheduling system if it allows waiting for the remaining jobs to complete before shutting down.

This method will be called just before all :any:`Inlet.on_shutdown` and :any:`Outlet.on_shutdown` are called.

Example from :any:`APSPlanner._shutdown_planner`:

.. code-block:: python

    def _shutdown_planner(self, wait:bool=True):
        self._scheduler.shutdown(wait=wait)



Exceptions
^^^^^^^^^^^^^^^^^

When implementing your planner you should consider that links may raise exceptions when executing. Your planner should anticipate this and allow handling the exceptions appropriately to ensure continuous execution. Both :any:`APSPlanner` and :any:`SchedulePlanner` allow catching exceptions when :code:`catch_exceptions=True` is passed on construction, otherwise they will log the exception and shutdown. See :ref:`Exception handling <exception_handling>` for more.

active property
^^^^^^^^^^^^^^^^^

Apart from extending the necessary methods described above, you may optionally implement the :any:`active` property. It should return a boolean value indicating whether the scheduler is currently running. This property is exposed for your convenience and is not used by Databay.


----

.. rubric:: Next Steps

#. Learn about extending :ref:`Inlets <extending_inlets>` and :ref:`Outlets <extending_outlets>`.
#. See the :any:`Examples <../examples>`


