"""
.. seealso:: :any:`BasePlanner` for remaining interface of this planner.
"""

import logging
import threading
import time
from concurrent import futures

import schedule

from databay.base_planner import BasePlanner
from databay import Link

_LOGGER = logging.getLogger('databay.SchedulePlanner')


class ScheduleIntervalError(Exception):
    """ Raised when link interval is smaller than the Schedule refresh interval."""
    pass

class SchedulePlanner(BasePlanner):
    """
    Planner implementing scheduling using Schedule_. Scheduling sets the :class:`Schedule's Job <schedule.Job>` as links' job.

    .. _Schedule: https://schedule.readthedocs.io/

    """

    def __init__(self, threads:int=30, refresh_interval:float=1.0, catch_exceptions:bool=False):
        """
        :type threads: :class:`int`
        :param threads: Number of threads to use.
            |default| :code:`30`
        
        :type refresh_interval: :class:`float`
        :param refresh_interval: Frequency at which this planner will scan over
            its links and attempt to update them if necessary. Note that adding
            links with interval smaller than this value will raise a :any:`ScheduleIntervalError`.
            |default| :code:`1.0`

        :type catch_exceptions: :class:`bool`
        :param catch_exceptions: Whether exceptions should be caught or halt the planner. |default| :code:`False`
        """

        super().__init__()
        self._running = False
        self._threads = threads
        self._refresh_interval = refresh_interval
        self._thread_pool = None
        self._exc_info = []
        self._exc_lock = threading.Lock()
        self._catch_exceptions = catch_exceptions

        # self._create_thread_pool()

    @property
    def refresh_interval(self) -> float:
        """

        Frequency at which this planner will scan over its links and attempt to update
        them if necessary. Note that adding links with interval smaller than this
        value will raise a :any:`ScheduleIntervalError`.

        :return: Refresh interval frequency.
        :rtype: float
        """

        return self._refresh_interval

    def _create_thread_pool(self):
        """
        Create a new thread pool.
        """

        self._thread_pool = futures.ThreadPoolExecutor(max_workers=self._threads)

    def _destroy_thread_pool(self, wait:bool=True):
        """
        Destroy the existing thread pool if one exists.

        :type wait: :class:`bool`
        :param wait: whether to wait for the existing thread pool to shut down.
        """

        if self._thread_pool is not None:
            self._thread_pool.shutdown(wait=wait)
            self._thread_pool = None

    def _try_job(self, link):
        try:
            link.transfer()
        except:
            import sys
            with self._exc_lock:
                self._exc_info.append((sys.exc_info(), link))

    def _run_job(self, link):
        self._thread_pool.submit(self._try_job, link)

    def _schedule(self, link:Link):
        """
        Schedule a link, setting a :class:`schedule.Job` as this link's job.

        :type link: :any:`Link`
        :param link: Link to be scheduled

        :raises: :class:`ScheduleIntervalError` if link's interval is smaller than the :any:`refresh interval`.
        """

        if link.interval.total_seconds() < self._refresh_interval:
            raise ScheduleIntervalError(f'Link interval must be greater than or equal to refresh interval. Link interval: {link.interval.total_seconds()}s, Refresh interval: {self._refresh_interval}s')

        job = schedule.every(link.interval.total_seconds()).seconds.do(self._run_job, link)
        link.set_job(job)

    def _unschedule(self, link):
        """
        Unschedule a link.

        :type link: :any:`Link`
        :param link: Link to be unscheduled
        """

        if link.job is not None:
            schedule.cancel_job(link.job)
            link.set_job(None)

    def start(self):
        """
        Start this planner. Links will start being scheduled based on their intervals
        after calling this method. Creates a new thread pool if one doesn't
        already exist.
        """

        super().start()

    def _start_planner(self):
        if self._running: return
        self._running = True

        if self._thread_pool is None:
            self._create_thread_pool()

        while self._running:
            schedule.run_pending()

            # handle exceptions raised by threads
            if len(self._exc_info) > 0:
                with self._exc_lock:
                    for exc_info in self._exc_info:
                        ex = exc_info[0][1]
                        extra_info = f'\n\nRaised when executing {exc_info[1]}'
                        exception_message = str(ex) + f'{extra_info}'
                        traceback = ex.__traceback__

                        try: # weird try/catch in order to get whole traceback into logger
                            try:
                                raise type(ex)(exception_message).with_traceback(traceback)
                            except TypeError as type_exception:
                                # Some custom exceptions won't let you use the common constructor and will throw an error on initialisation. We catch these and just throw a generic RuntimeError.
                                if 'required positional argument' in str(type_exception):
                                    raise RuntimeError(exception_message).with_traceback(traceback) from None
                        except Exception as e:
                            if self._catch_exceptions:
                                _LOGGER.exception(e)
                            else:
                                raise e

                    self._exc_info = []

            # TODO: adjust interval to avoid drift - look how APS does it in BlockingScheduler
            time.sleep(self._refresh_interval)

    def shutdown(self, wait:bool=True):
        """
        Stop this planner. Links will stop being scheduled after calling this method

        :type wait: :class:`bool`
        :param wait: Whether to wait until all currently executing jobs have finished.
            |default| :code:`True`
        """
        super().shutdown(wait)

    def _shutdown_planner(self, wait:bool=True):
        self._running = False
        self._destroy_thread_pool(wait=wait)

    @property
    def running(self): # pragma: no cover
        """
        Whether this planner is currently running. If there are links transferring this may be set before all transfers are complete. Changed by calls to :any:`start` and :any:`shutdown`.

        :return: State of this planner
        :rtype: :any:`bool`
        """
        return self._running

    def __repr__(self):
        return 'SchedulePlanner(threads:%s, refresh_interval:%s)' \
               % (self._threads, self.refresh_interval)

