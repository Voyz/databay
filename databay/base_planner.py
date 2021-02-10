"""
.. seealso::

    :ref:`Extending BasePlanner <extending_base_planner>` to learn how to extend this class correctly.
"""
import atexit
import logging
from abc import ABC, abstractmethod
from typing import List, Union

from databay.errors import MissingLinkError
from databay.link import Link

_LOGGER = logging.getLogger('databay.BasePlanner')


class BasePlanner(ABC):
    """
    Base abstract class for a job planner. Implementations should handle scheduling link transfers based on :py:class:`datetime.timedelta` intervals.
    """


    def __init__(self, links: Union[Link, List[Link]] = None, ignore_exceptions: bool = False, immediate_transfer: bool = True, shutdown_at_exit : bool = False):
        """
        :type links: :any:`Link` or list[:any:`Link`]
        :param links: Links that should be added and scheduled.

        :type ignore_exceptions: :class:`bool`
        :param ignore_exceptions: Whether exceptions should be ignored, or halt the planner.
            |default| :code:`False`

        :type immediate_transfer: :class:`bool`
        :param immediate_transfer: Whether planner should execute one transfer immediately upon starting.
            |default| :code:`True`
            
        :type shutdown_at_exit: bool
        :param shutdown_at_exit: Whether this planner should attempt to gracefully shutdown if the app exists unexpectedly.
            |default| :code:`False`
        """
        self._links = []
        if links is not None:
            self.add_links(links)

        self.immediate_transfer = immediate_transfer
        self._ignore_exceptions = ignore_exceptions
        self.shutdown_at_exit = shutdown_at_exit
        atexit.register(self._at_exit_callback)


    @property
    def links(self):
        """
        Links currently handled by this planner.

        :return: list[:any:`Link`]
        """
        return self._links

    def add_links(self, links: Union[Link, List[Link]]):
        """
        Add new links to this planner. This can be run once planner is already running.

        :type links: :any:`Link` or list[:any:`Link`]
        :param links: Links that should be added and scheduled.
        """
        if not isinstance(links, list):
            links = [links]

        for link in links:
            assert isinstance(link, Link)
            self._links.append(link)
            self._schedule(link)
            _LOGGER.info('Added link: %s', link)

    def remove_links(self, links: Link):
        """
        Remove links from this planner. This can be run once planner is already running.

        :type links: :any:`Link` or list[:any:`Link`]
        :param links: Links that should be unscheduled and removed.

        :raises: :py:class:`MissingLinkError <errors.MissingLinkError>` if link is not found.
        """
        if not isinstance(links, list):
            links = [links]

        for link in links:
            if link not in self._links:
                raise MissingLinkError(
                    f'Planner does not contain the link: {link}')

            if link.job is not None:
                self._unschedule(link)

            self._links.remove(link)

    @abstractmethod
    def _schedule(self, link: Link):
        """
        Schedule a link. Note that links expect to be given a job upon scheduling by calling :py:func:`Link.set_job <databay.link.Link.set_job>` method.

        Override this method to provide scheduling logic.

        :type link: :any:`Link`
        :param link: Link to be scheduled
        """
        raise NotImplementedError() # pragma: no cover

    @abstractmethod
    def _unschedule(self, link: Link):
        """
        Unschedule a link.

        Override this method to provide unscheduling logic.

        :type link: :any:`Link`
        :param link: Link to be unscheduled
        """
        raise NotImplementedError() # pragma: no cover

    def start(self):
        """
        Start this planner. Links will start being scheduled based on their intervals after calling this method. The exact methodology depends on the planner implementation used.

        This will also loop over all links and call the on_start callback before starting the planner.

        If :any:`BasePlanner.immediate_transfer` is set to True, this function will additionally call :any:`Link.transfer` once for each link managed by this planner before starting.

        See :ref:`Start and Shutdown <start_shutdown>` to learn more about starting and shutdown.
        """
        _LOGGER.info('Starting %s' % str(self))
        for link in self.links:
            try:
                link.on_start()
            except Exception as e:
                try:
                    raise RuntimeError(f'on_start link exception: "{e}" for link: {link}') from e
                except Exception as ee:
                    self._on_exception(ee, link)

        if self.immediate_transfer:
            for link in self.links:
                try:
                    link.transfer()
                except Exception as e:
                    self._on_exception(e, link)

                    if not self._ignore_exceptions:
                        return

        self._start_planner()

    def shutdown(self, wait: bool = True):
        """
        Shutdown this planner. Links will stop being scheduled after calling this method. Remaining link jobs may still execute after calling this method depending on the concrete planner implementation.

        This will also loop over all links and call the on_shutdown callback after shutting down the planner.

        See :ref:`Start and Shutdown <start_shutdown>` to learn more about starting and shutdown.
        """
        _LOGGER.info('Shutting down %s' % str(self))
        self._shutdown_planner(wait)
        for link in self.links:
            link.on_shutdown()

    @abstractmethod
    def _start_planner(self):
        """
        Override this method to provide starting functionality.
        """
        raise NotImplementedError() # pragma: no cover

    @abstractmethod
    def _shutdown_planner(self, wait: bool = True):
        """
        Override this method to provide shutdown functionality.
        """
        raise NotImplementedError() # pragma: no cover

    def _on_exception(self,
                      exception : Exception,
                      link : Link = None):
        """
        Override this method to provide exception handling functionality
        """
        try: # weird try/catch in order to get whole traceback into logger
            extra_info = f'\n\nRaised when executing {link}'
            exception_message = str(exception) + f'{extra_info}'
            traceback = exception.__traceback__

            try:
                raise type(exception)(
                    exception_message).with_traceback(traceback)
            except TypeError as type_exception:
                # Some custom exceptions won't let you use the common constructor and will throw an error on initialisation. We catch these and just throw a generic RuntimeError.
                raise RuntimeError(exception_message).with_traceback(
                    traceback) from None
        except Exception as e:
            _LOGGER.exception(e)

        if not self._ignore_exceptions and self.running:
            self.shutdown(wait=False)

    def purge(self):
        """
        Unschedule and clear all links. It can be used while planner is running.
        """
        for link in self.links:
            self._unschedule(link)

        self._links = []

    @property
    @abstractmethod
    def running(self):
        """
        Whether this planner is currently running.

        By default always returns True.

        Override this property to indicate when the underlying scheduling functionality is currently running.
        """
        return True

    def __repr__(self):
        return f"BasePlanner(links={len(self.links)}, shutdown_at_exit={self.shutdown_at_exit})"


    def _at_exit_callback(self):
        """
        Callback used when the process is exiting, used to attempt a graceful shutdown.
        """
        if self.shutdown_at_exit and self.running:
            _LOGGER.info(f'Attempting to shutdown planner "{self}" gracefully.')
            self.shutdown(True)

