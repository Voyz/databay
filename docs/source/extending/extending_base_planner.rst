Extending BasePlanner
=====================

Databay comes with two implementations of BasePlanner - :any:`APSPlanner` and :any:`SchedulePlanner`. If you require custom scheduling functionality outside of these two interfaces, you can create your own implementation of :any:`BasePlanner`. Have a look at the two existing implementations for reference: `APSPlanner <../_modules/databay/planners/aps_planner.html>`_ and `SchedulePlanner <../_modules/databay/planners/schedule_planner.html>`_.

To extend the :any:`BasePlanner` you need to provide a way of executing :any:`Link.transfer` method repeatedly by implementing the following four methods. Note that all of these functions are private since they are called internally by BasePlanner and should not be executed directly.

.. contents::
    :local:
    :backlinks: entry


_schedule
^^^^^^^^^

Schedule a :any:`Link`. This function runs whenever :any:`add_link` is called and should not be called directly. It should accept a link and add its :any:`transfer` method to the scheduling system you're using. Note that you do not need to store the link in your planner - BasePlanner will automatically store it under :any:`BasePlanner.links` when :any:`add_link` is called.

Each link comes with a :any:`datetime.timedelta` interval at which it should be run. Use :any:`Link.interval` and schedule according to the interval specified. The function that needs to execute on that interval is :any:`Link.transfer`.

It isn't required for the scheduling to be already running when :code:`_schedule` is called.

If the scheduler you're using utilises some form of task-managing objects such as :code:`Jobs`, you must assign that job object to the link being scheduled using :any:`Link.set_job`. This is to ensure the job can be correctly destroyed later when :any:`remove_link <BasePlanner.remove_link>` is called.

Example from :any:`APSPlanner._schedule`:

.. code-block:: python

    def _schedule(self, link:Link):
        job = self._scheduler.add_job(link.transfer,
            trigger=IntervalTrigger(seconds=link.interval.total_seconds()))

        link.set_job(job)


_unschedule
^^^^^^^^^^^

Unschedule a :any:`Link`. This function runs whenever :any:`remove_link` is called and should not be called directly. It should accept a link and remove it to the scheduling system you're using. Note that you do not need to remove the link from your planner - BasePlanner will automatically remove that link from :any:`BasePlanner.links` when :any:`remove_link` is called.

It isn't required for the scheduling to be already stopped when :code:`_unschedule` is called.

If the scheduler you're using utilises some form of task-managing objects such as :code:`Jobs`, you must destroy that job object that is attached to the link through :any:`Link.job`. This is to ensure the job can be correctly destroyed when :any:`_unschedule` is called.

Example from :any:`APSPlanner._unschedule`:

.. code-block:: python

    def _unschedule(self, link:Link):
        if link.job is not None:
            link.job.remove()
            link.set_job(None)

_start_planner
^^^^^^^^^^^^^^

Start the scheduling. This function runs whenever :any:`start` is called and should not be called directly. It should begin the scheduling of links.

This function will be called just after all :any:`Inlet.on_start` and :any:`Outlet.on_start` are called.

Example from :any:`APSPlanner._start_planner`:

.. code-block:: python

    def _start_planner(self):
        self._scheduler.start()

_shutdown_planner
^^^^^^^^^^^^^^^^^

Shutdown the scheduling. This function runs whenever :any:`shutdown` is called and should not be called directly. It should shutdown the scheduling of links.

This function is called with :code:`wait` parameter that you can pass down to your scheduling system if it allows waiting for the remaining jobs to complete before shutting down.

This function will be called just before all :any:`Inlet.on_shutdown` and :any:`Outlet.on_shutdown` are called.

Example from :any:`APSPlanner._shutdown_planner`:

.. code-block:: python

    def _shutdown_planner(self, wait:bool=True):
        self._scheduler.shutdown(wait=wait)


----

.. rubric:: active

Apart from extending the necessary methods described above, you may optionally implement the :any:`active` property. It should return a boolean value indicating whether the scheduler is currently running. This function is exposed for your convenience and is not used by Databay.