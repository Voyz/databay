"""
.. seealso::

    :ref:`Extending BasePlanner <extending_base_planner>` to learn how to extend this class correctly.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Union

from databay.errors import MissingLinkError
from databay.link import Link

_LOGGER = logging.getLogger('databay.BasePlanner')

class BasePlanner(ABC):
    """
    Base abstract class for a job planner. Implementations should handle scheduling link updates based on :py:class:`datetime.timedelta` intervals.
    """


    def __init__(self, links:Union[Link, List[Link]]=None):
        """
        :type links: :any:`Link` or list[:any:`Link`]
        :param links: Links that should be added and scheduled.
        """

        self._links = []
        if links is not None:
            self.add_links(links)

    @property
    def links(self):
        """
        Links currently handled by this planner.

        :return: list[:any:`Link`]
        """
        return self._links

    def add_links(self, links:Union[Link, List[Link]]):
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

        See :ref:`Start and Shutdown <start_shutdown>` to learn more about starting and shutdown.
        """
        _LOGGER.info('Starting %s' % str(self))
        for link in self.links:
            link.on_start()
        self._start_planner()

    def shutdown(self, wait:bool=True):
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