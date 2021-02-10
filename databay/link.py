import asyncio
import copy
import datetime
import itertools
import warnings
import logging
import warnings
from typing import Any, List, Union

from databay import Inlet, Outlet
from databay.errors import InvalidNodeError
_LOGGER = logging.getLogger('databay.Link')


class Update():
    """
    Data structure representing one Link transfer. When converted to string returns :code:`{tags}.{transfer_number}`
    """

    def __init__(self, tags: List[str], transfer_number: int):
        """

        :type tags: List[str]
        :param tags: Tags of the link, see: :class:`Link`.

        :type transfer_number: int
        :param transfer_number: Incremental identifier of the current transfer.
        """
        self.tags = tags
        self.transfer_number = transfer_number

    def __repr__(self):
        """
        Provides the formatted transfer string.

        :returns: "{tags}.{transfer_number}"
        """
        s = ''
        if self.tags != []:
            s += f'{".".join(self.tags)}.'
        s += f'{self.transfer_number}'
        return s

from databay import Inlet, Outlet

class Link():
    """
    Link in the relationship graph. Use this class to define relationships between inlets and outlets.
    """

    def __init__(self,
                 inlets: Union[Inlet, List[Inlet]],
                 outlets: Union[Outlet, List[Outlet]],
                 interval: Union[datetime.timedelta, int, float],
                 tags: Union[str, List[str]] = None,
                 copy_records: bool = True,
                 ignore_exceptions: bool = False,
                 catch_exceptions: bool = None,
                 inlet_concurrency : int = 9999,
                 name=None):
        """
        :type inlets: :any:`Inlet` or list[:any:`Inlet`]
        :param inlets: inlets to add to this link.

        :type outlets: :any:`Outlet` or list[:any:`Outlet`]
        :param outlets: outlets to add to this link.

        :type interval: Union[datetime.timedelta, int, float]
        :param interval: Expects :code:`datetime.timedelta`. Alternatively, you can provide :code:`int` or :code:`float` which will be coerced explicitly to :code:`datetime.timedelta.seconds`.

        :type tags: Union[str, List[str]]
        :param tags: List of tags of this link. |default| :code:`[]`

        :type copy_records: bool
        :param copy_records: Whether to copy records before passing them to outlets. |default| :code:`True`

        :type ignore_exceptions: bool
        :param ignore_exceptions: Whether exceptions in inlets and outlets should be logged and ignored, or raised. |default| :code:`True`

        :type inlet_concurrency: int
        :param inlet_concurrency: How many inlets are allowed to execute concurrently. |default| :code:`9999`
        """

        self._inlets = []
        self._outlets = []
        self.add_inlets(inlets)
        self.add_outlets(outlets)
        if isinstance(interval, (int, float)):
            self._interval = datetime.timedelta(seconds=interval)
        else:
            self._interval = interval
        self._transfer_number = -1
        self._job = None
        if name != None:
            warnings.warn(
                '\'name\' parameter was deprecated in 0.2.0 and will be removed in version 1.0. Use \'tags\' instead.')
            tags = [name]

        if isinstance(tags, str):
            tags = [tags]
        self._tags = tags if tags is not None else []
        self._copy_records = copy_records
        self._ignore_exceptions = ignore_exceptions
        if catch_exceptions is not None:  # pragma: no cover
            self._ignore_exceptions = catch_exceptions
            warnings.warn(
                '\'catch_exceptions\' was renamed to \'ignore_exceptions\' in version 0.2.0 and will be permanently changed in version 1.0.0', DeprecationWarning)

        self.inlet_concurrency = inlet_concurrency

    @property
    def inlets(self) -> List[Inlet]:
        """
        Inlets handled by this link.

        :returns: list[:any:`Inlet`]
        """
        return self._inlets

    def add_inlets(self, inlets: Union[Inlet, List[Inlet]]):
        """
        Add inlets to this link. Inlets must be of type Inlet and not currently added to this link.

        :type inlets: :any:`Inlet` or list[:any:`Inlet`]
        :param inlets: inlets to add to this link

        :raises: :any:`InvalidNodeError` if this link already contains any of the inlets being added.
        """
        if not isinstance(inlets, list):
            inlets = [inlets]

        for inl in inlets:
            if not isinstance(inl, Inlet):
                raise TypeError(f"Provided inlet is not an instance of Inlet(), found: {inl}")

            if inl in self._inlets:
                raise InvalidNodeError(
                    'Link already contains inlet: %s' % (inl))

        self._inlets = self._inlets + inlets

    def remove_inlets(self, inlets: Union[Inlet, List[Inlet]]):
        """
        Remove inlets from this link.

        :type inlets: :any:`Inlet` or list[:any:`Inlet`]
        :param inlets: inlets to remove from this link

        :raises: :any:`InvalidNodeError` if this link doesn't contain any of the inlets being removed.
        """
        if not isinstance(inlets, list):
            inlets = [inlets]

        for inl in inlets:
            if inl not in self._inlets:
                raise InvalidNodeError(
                    'Link does not contain inlet: %s' % (inl))

            self._inlets.remove(inl)

    @property
    def outlets(self) -> List[Outlet]:
        """
        Outlets handled by this link.

        :returns: list[:any:`Outlet`]
        """
        return self._outlets

    def add_outlets(self, outlets: Union[Outlet, List[Outlet]]):
        """
        Add outlets to this link. Outlets must be of type Outlet and not currently added to this link.

        :type outlets: :any:`Outlet` or list[:any:`Outlet`]
        :param outlets: outlets to add to this link

        :raises: :any:`InvalidNodeError` if this link already contains any of the outlets being added.
        """
        if not isinstance(outlets, list):
            outlets = [outlets]

        for outl in outlets:
            if not isinstance(outl, Outlet):
                raise TypeError(f"Provided outlet is not an instance of Outlet(), found: {outl}")

            if outl in self._outlets:
                raise InvalidNodeError(
                    'Link already contains outlet: %s' % (outl))

        self._outlets = self._outlets + outlets

    def remove_outlets(self, outlets: Union[Outlet, List[Outlet]]):
        """
        Remove outlets from this link.

        :type outlets: :any:`Outlet` or list[:any:`Outlet`]
        :param outlets: outlets to remove from this link

        :raises: :any:`InvalidNodeError` if this link doesn't contain any of the outlets being removed.
        """
        if not isinstance(outlets, list):
            outlets = [outlets]

        for outl in outlets:
            if outl not in self._outlets:
                raise InvalidNodeError(
                    'Link does not contain outlet: %s' % (outl))

            self._outlets.remove(outl)

    @property
    def interval(self) -> datetime.timedelta:
        """
        Frequency at which this link should transfer.

        :returns: interval object
        :rtype: :class:`datetime.timedelta`
        """
        return self._interval

    def set_job(self, job):  # pragma: no cover
        """
        :type job: Any
        :param job: specify the job this link is executed with.
        """
        self._job = job

    @property
    def job(self) -> Any:  # pragma: no cover
        """
        The job this link is executed with. Job should persist between link transfers.
        |default| :code:`None`

        :returns: Job this link is executed with.
        """
        return self._job

    @property
    def name(self) -> str:
        """
        Deprecated in 0.2.0, will be removed in 1.0. Use :any:`Link.tags` instead.

        Name of this Link, equivalent to first tag of this link.

        :returns: Name of this link
        :rtype: str
        """
        warnings.warn(
            '\'Link.name\' property was deprecated in 0.2.0 and will be removed in version 1.0. Use \'Link.tags\' instead.')
        return self.tags[0] if len(self.tags) else ''

    @property
    def tags(self) -> List[str]:
        """
        The tags of this link. |default| :code:`[]`

        :returns: Tags of this link
        :rtype: List[str]
        """
        return self._tags

    def transfer(self):
        """
        Execute one transfer on this link. This will run through all inlets querying them for data, then pass that data to all outlets.

        See :ref:`Link transfer <link_transfer>` to learn more about the transfer.
        """
        asyncio.run(self._run())

    async def _run(self):
        """
        Coroutine handling the transfer.
        """
        semaphore = asyncio.Semaphore(self.inlet_concurrency)
        self._transfer_number += 1
        update = Update(tags=self.tags, transfer_number=self._transfer_number)
        _LOGGER.debug(f'{update} transfer')

        async def inlet_task(inlet):
            try:
                async with semaphore:
                    return await inlet._pull(update)
            except Exception as e:
                if self._ignore_exceptions:
                    _LOGGER.exception(
                        f'Inlet exception: "{e}" for inlet: {inlet}, in: {self}, during: {update}', exc_info=True)
                    return []
                else:
                    raise e

        inlet_tasks = [inlet_task(inlet) for inlet in self._inlets]
        results_raw = await asyncio.gather(*inlet_tasks)
        records = list(itertools.chain.from_iterable(results_raw))

        async def outlet_task(outlet, records_copy):
            try:
                await outlet._push(records_copy, update)
            except Exception as e:
                if self._ignore_exceptions:
                    _LOGGER.exception(
                        f'Outlet exception: "{e}" for outlet: {outlet}, in link: {self}, during: {update}', exc_info=True)
                else:
                    raise e

        outlet_tasks = []
        for outlet in self._outlets:
            if self._copy_records:
                task = outlet_task(outlet, copy.deepcopy(records))
            else:
                task = outlet_task(outlet, records)
            outlet_tasks.append(task)
        await asyncio.gather(*outlet_tasks)

        _LOGGER.debug(f'{update} done')

    def on_start(self):
        """
        Called when the governing planner is about to start.
        Calls :any:`try_start <Inlet.try_start>` on all inlets and outlets of this link.

        If an inlet or outlet is present in multiple links its on_start will only be called
        once by whichever link executes first.
        """

        for inlet in self._inlets:
            try:
                inlet.try_start()
            except Exception as e:
                if self._ignore_exceptions:
                    _LOGGER.exception(
                        f'on_start inlet exception: "{e}" for inlet: {inlet}, in link: {self}',
                        exc_info=True)
                else:
                    raise e

        for outlet in self._outlets:
            try:
                outlet.try_start()
            except Exception as e:
                if self._ignore_exceptions:
                    _LOGGER.exception(
                        f'on_start outlet exception: "{e}" for outlet: {outlet}, in link: {self}',
                        exc_info=True)
                else:
                    raise e

    def on_shutdown(self):
        """
        Called just after the governing planner has shutdown.
        Calls :any:`try_shutdown <Inlet.try_shutdown>` on all inlets and outlets of this link.

        If an inlet or outlet is present in multiple links its on_shutdown will only be called
        once by whichever link executes first.
        """

        for inlet in self._inlets:
            try:
                inlet.try_shutdown()
            except Exception as e:
                if self._ignore_exceptions:
                    _LOGGER.exception(
                        f'on_shutdown inlet exception: "{e}" for inlet: {inlet}, in link: {self}',
                        exc_info=True)
                else:
                    raise e

        for outlet in self._outlets:
            try:
                outlet.try_shutdown()
            except Exception as e:
                if self._ignore_exceptions:
                    _LOGGER.exception(
                        f'on_shutdown outlet exception: "{e}" for outlet: {outlet}, in link: {self}',
                        exc_info=True)
                else:
                    raise e

    def __repr__(self):
        """
        :returns: Link(tags:%s, inlets:%s, outlets:%s, interval:%s)
        """

        return 'Link(tags:%s, inlets:%s, outlets:%s, interval:%s)' % (self.tags, self.inlets, self.outlets, self.interval)
