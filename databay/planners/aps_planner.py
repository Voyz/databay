"""
.. seealso::
    * :ref:`Scheduling <scheduling>` to learn more about scheduling in Databay.
    * :any:`BasePlanner` for the remaining interface of this planner.
"""

import logging
import warnings
from typing import Union, List

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from databay.base_planner import BasePlanner
from databay import Link

_LOGGER = logging.getLogger('databay.ApsPlanner')
# We ignore the APScheduler's exceptions because we log them ourselves.
logging.getLogger('apscheduler.executors').setLevel(logging.CRITICAL)

warnings.filterwarnings("always", category=DeprecationWarning,
                        module=__name__)


class ApsPlanner(BasePlanner):
    """
    Planner implementing scheduling using the |APS|_. Scheduling sets the :any:`APS Job <apscheduler.job.Job>` as links' job.

    .. |APS| replace:: Advanced Python Scheduler
    .. _APS: https://apscheduler.readthedocs.io/en/stable/index.html
    .. _configuring-scheduler: https://apscheduler.readthedocs.io/en/stable/userguide.html#configuring-the-scheduler

    """

    def __init__(self, links: Union[Link, List[Link]] = None, threads: int = 30, executors_override: dict = None, job_defaults_override: dict = None, ignore_exceptions: bool = False, catch_exceptions: bool = None):
        """

        :type links: :any:`Link` or list[:any:`Link`]
        :param links: Links that should be added and scheduled.
            |default| :code:`None`

        :type threads: int
        :param threads: Number of threads available for job execution. Each link will be run on a separate thread job.
            |default| :code:`30`

        :type executors_override: dict
        :param executors_override: Overrides for executors option of `APS configuration <configuring-scheduler_>`__
            |default| :code:`None`

        :type job_defaults_override: dict
        :param job_defaults_override: Overrides for job_defaults option of `APS configuration <configuring-scheduler_>`__
            |default| :code:`None`

        :type ignore_exceptions: bool
        :param ignore_exceptions: Whether exceptions should be ignored or halt the planner.
            |default| :code:`False`
        """

        self._threads = threads
        self._ignore_exceptions = ignore_exceptions
        if catch_exceptions is not None:  # pragma: no cover
            self._ignore_exceptions = catch_exceptions
            warnings.warn(
                '\'catch_exceptions\' was renamed to \'ignore_exceptions\' in version 0.2.0 and will be permanently changed in version 1.0.0', DeprecationWarning)

        if executors_override is None:
            executors_override = {}
        if job_defaults_override is None:
            job_defaults_override = {}

        executors = {'default': ThreadPoolExecutor(
            threads), **executors_override}
        job_defaults = {'coalesce': False,
                        'max_instances': threads, **job_defaults_override}

        self._scheduler = BlockingScheduler(
            executors=executors, job_defaults=job_defaults, timezone='UTC')
        # self._scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
        self._scheduler.add_listener(self._on_exception, EVENT_JOB_ERROR)

        super().__init__(links)

    def _on_exception(self, event):
        if event.code is EVENT_JOB_ERROR:
            try:
                # It would be amazing if we could print the entire Link, but APS serialises Link.transfer to a string and that's all we have from Job's perspective.
                extra_info = f'\n\nRaised when executing {self._scheduler.get_job(event.job_id)}'
                exception_message = str(event.exception) + f'{extra_info}'
                traceback = event.exception.__traceback__

                try:
                    raise type(event.exception)(
                        exception_message).with_traceback(traceback)
                except TypeError as type_exception:
                    # Some custom exceptions won't let you use the common constructor and will throw an error on initialisation. We catch these and just throw a generic RuntimeError.
                    raise Exception(exception_message).with_traceback(
                        traceback) from None
            except Exception as e:
                _LOGGER.exception(e)

            if not self._ignore_exceptions and self.running:
                self.shutdown(wait=False)

    def _schedule(self, link: Link):
        """
        Schedule a link. Sets :any:`APS Job <apscheduler.job.Job>` as this link's job.

        :type link: :any:`Link`
        :param link: Link to be scheduled
        """

        job = self._scheduler.add_job(link.transfer, trigger=IntervalTrigger(
            seconds=link.interval.total_seconds()))
        link.set_job(job)

    def _unschedule(self, link: Link):
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

        See :ref:`Start and Shutdown <start_shutdown>` to learn more about starting and shutdown.
        """
        super().start()

    def _start_planner(self):
        self._scheduler.start()

    def pause(self):
        """
        Pause this planner. Calls :any:`APScheduler.pause() <apscheduler.schedulers.base.BaseScheduler.pause>`
        """
        _LOGGER.info('Pausing %s' % str(self))
        self._scheduler.pause()

    def resume(self):
        """
        Resume this planner. Calls :any:`APScheduler.resume() <apscheduler.schedulers.base.BaseScheduler.resume>`
        """
        _LOGGER.info('Resuming %s' % str(self))
        self._scheduler.resume()

    def shutdown(self, wait: bool = True):
        """
        Shutdown this planner. Calls :any:`APScheduler.shutdown() <apscheduler.schedulers.base.BaseScheduler.shutdown>`

        See :ref:`Start and Shutdown <start_shutdown>` to learn more about starting and shutdown.

        :type wait: bool
        :param wait: Whether to wait until all currently executing jobs have finished.
            |default| :code:`True`
        """
        super().shutdown(wait)

    def _shutdown_planner(self, wait: bool = True):
        """
        Shutdown this planner. Calls :any:`APScheduler.shutdown() <apscheduler.schedulers.base.BaseScheduler.shutdown>`

        :type wait: bool
        :param wait: Whether to wait until all currently executing jobs have finished.
            |default| :code:`True`
        """
        self._scheduler.shutdown(wait=wait)

    def purge(self):
        """
        Unschedule and clear all links. It can be used while planner is running. APS automatically removes jobs, so we only clear the links.
        """
        for link in self.links:
            try:
                link.job.remove()
            except JobLookupError:
                pass  # APS already removed jobs if shutdown was called before purge, otherwise let's do it ourselves
            link.set_job(None)

        self._links = []

    @property
    def running(self):
        """
        Whether this planner is currently running. Changed by calls to :any:`start` and :any:`shutdown`.


        :return: State of this planner
        :rtype: bool
        """
        return self._scheduler.state == STATE_RUNNING

    def __repr__(self):
        return 'ApsPlanner(threads:%s)' % (self._threads)


class APSPlanner(ApsPlanner):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        warnings.warn(
            'APSPlanner was renamed to ApsPlanner in version 0.1.7 and will be permanently changed in version 1.0', DeprecationWarning)
        super().__init__(*args, **kwargs)
