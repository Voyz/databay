"""
.. seealso:: :any:`BasePlanner` for remaining interface of this planner.
"""

import logging

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pytz import utc

from databay.base_planner import BasePlanner
from databay import Link

_LOGGER = logging.getLogger('databay.APSPlanner')
# We ignore the APScheduler's exceptions because we log them ourselves.
logging.getLogger('apscheduler.executors').setLevel(logging.CRITICAL)

class APSPlanner(BasePlanner):
    """
    Planner implementing scheduling using the |APS|_. Scheduling sets the :any:`APS Job <apscheduler.job.Job>` as links' job.

    .. |APS| replace:: Advanced Python Scheduler
    .. _APS: https://apscheduler.readthedocs.io/en/stable/index.html
    .. _configuring-scheduler: https://apscheduler.readthedocs.io/en/stable/userguide.html#configuring-the-scheduler

    """

    def __init__(self, threads:int=30, executors_override:dict=None, job_defaults_override:dict=None, catch_exceptions:bool=False):
        """

        :type threads: :class:`int`
        :param threads: Number of threads available for job execution. Each link will be run on a separate thread job. |default| :code:`30`

        :type executors_override: :class:`dict`
        :param executors_override: Overrides for executors option of `APS configuration <configuring-scheduler_>`__ |default| :code:`None`

        :type job_defaults_override: :class:`dict`
        :param job_defaults_override: Overrides for job_defaults option of `APS configuration <configuring-scheduler_>`__  |default| :code:`None`

        :type catch_exceptions: :class:`bool`
        :param catch_exceptions: Whether exceptions should be caught or halt the planner. |default| :code:`False`
        """

        super().__init__()
        self._threads = threads
        self._catch_exceptions = catch_exceptions

        if executors_override is None: executors_override = {}
        if job_defaults_override is None: job_defaults_override = {}

        executors = {'default': ThreadPoolExecutor(threads), **executors_override}
        job_defaults = {'coalesce': False, 'max_instances': threads, **job_defaults_override}

        self._scheduler = BlockingScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
        # self._scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
        self._scheduler.add_listener(self._on_exception, EVENT_JOB_ERROR)

    def _on_exception(self, event):
        if event.code is EVENT_JOB_ERROR:
            try:
                extra_info = f'\n\nRaised when executing {self._scheduler.get_job(event.job_id)}'
                raise type(event.exception)(str(event.exception) + f'{extra_info}').with_traceback(event.exception.__traceback__)
            except Exception as e:
                _LOGGER.error(e, exc_info=True)

            if not self._catch_exceptions:
                self.shutdown(False)



    def _schedule(self, link:Link):
        """
        Schedule a link. Sets :any:`APS Job <apscheduler.job.Job>` as this link's job.

        :type link: :any:`Link`
        :param link: Link to be scheduled
        """

        job = self._scheduler.add_job(link.transfer, trigger=IntervalTrigger(seconds=link.interval.total_seconds()))
        link.set_job(job)


    def _unschedule(self, link:Link):
        """
        Unschedule a link.

        :type link: :any:`Link`
        :param link: Link to be unscheduled
        """
        if link.job is not None:
            link.job.remove()
            link.set_job(None)


    def start(self):
        """
        Start this planner. Calls :any:`APS Scheduler.start() <apscheduler.schedulers.base.BaseScheduler.start>`
        """
        super().start()


    def _start_planner(self):
        self._scheduler.start()


    def pause(self):
        """
        Pause this planner. Calls :any:`APS Scheduler.pause() <apscheduler.schedulers.base.BaseScheduler.pause>`
        """
        _LOGGER.info('Pausing %s' % str(self))
        self._scheduler.pause()


    def resume(self):
        """
        Resume this planner. Calls :any:`APS Scheduler.resume() <apscheduler.schedulers.base.BaseScheduler.resume>`
        """
        _LOGGER.info('Resuming %s' % str(self))
        self._scheduler.resume()


    def shutdown(self, wait:bool=True):
        """
        Shutdown this planner. Calls :any:`APS Scheduler.shutdown() <apscheduler.schedulers.base.BaseScheduler.shutdown>`

        :type wait: :class:`bool`
        :param wait: Whether to wait until all currently executing jobs have finished.
            |default| :code:`True`
        """
        super().shutdown(wait)

    def _shutdown_planner(self, wait:bool=True):
        """
        Shutdown this planner. Calls :any:`APS Scheduler.shutdown() <apscheduler.schedulers.base.BaseScheduler.shutdown>`

        :type wait: :class:`bool`
        :param wait: Whether to wait until all currently executing jobs have finished.
            |default| :code:`True`
        """
        self._scheduler.shutdown(wait=wait)

    @property
    def running(self):
        """
        Whether this planner is currently running. Changed by calls to :any:`start` and :any:`shutdown`.


        :return: State of this planner
        :rtype: :any:`bool`
        """
        return self._scheduler.state == STATE_RUNNING

    def __repr__(self):
        return 'APSPlanner(threads:%s)' % (self._threads)
