import logging
from abc import ABC, abstractmethod

from databay.errors import MissingLinkError
from databay.link import Link

_LOGGER = logging.getLogger('databay.BasePlanner')

class BasePlanner(ABC):
    """
    Base abstract class for a job planner. Implementations should handle scheduling link updates based on :py:class:`datetime.timedelta` intervals.
    """


    def __init__(self,):
        ""
        self._links = []

    @property
    def links(self):
        """
        Links currently handled by this planner.

        :return: list[:any:`Link`]
        """
        return self._links

    def add_link(self, link: Link):
        """
        Add new link to this planner. This can be run once planner is already running.

        :type link: :any:`Link`
        :param link: Link that should be added and scheduled.
        """
        self._links.append(link)
        self._schedule(link)
        _LOGGER.info('Added link: %s', link)

    def remove_link(self, link: Link):
        """
        Remove a link from this planner. This can be run once planner is already running.

        :type link: :any:`Link`
        :param link: Link that should be unscheduled and removed.

        :raises: :py:class:`MissingLinkError <errors.MissingLinkError>` if link is not found.
        """

        if link not in self._links:
            raise MissingLinkError(f'Planner does not contain the link: {link}')

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
        raise NotImplementedError()

    @abstractmethod
    def _unschedule(self, link: Link):
        """
        Unschedule a link.

        Override this method to provide unscheduling logic.

        :type link: :any:`Link`
        :param link: Link to be unscheduled
        """
        raise NotImplementedError()

    def start(self):
        """
        Start this planner. Links will start being scheduled based on their intervals after calling this method. The exact methodology depends on the planner implementation used.

        This will also loop over all links and call the on_start callback before starting the planner.
        """
        _LOGGER.info('Starting %s' % str(self))
        for link in self.links:
            link.on_start()
        self._start_planner()

    def shutdown(self, wait:bool=True):
        """
        Shutdown this planner. Links will stop being scheduled after calling this method. Remaining link jobs may still execute after calling this method depending on the concrete planner implementation.

        This will also loop over all links and call the on_shutdown callback after shutting down the planner.
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
        raise NotImplementedError()

    @abstractmethod
    def _shutdown_planner(self, wait:bool=True):
        """
        Override this method to provide shutdown functionality.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def running(self):
        """
        Whether this planner is currently running.

        Override this property to indicate when the underlying scheduling functionality is currently running.
        """
        raise NotImplementedError()