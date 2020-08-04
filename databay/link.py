import copy
import datetime
import itertools
from typing import List, Union, Any

import asyncio

import logging

from databay.errors import InvalidNodeError

_LOGGER = logging.getLogger('databay.Link')

class Update():
    """
    Data structure representing one Link transfer.
    """
    def __init__(self, name:str, index:int):
        """

        :type name: str
        :param name: Human readable identifier of the link, see: :class:`Link`.

        :type index: int
        :param index: Integer identifier of the current transfer.
        """
        self.name = name
        self.index = index

    def __repr__(self):
        """
        Provides the formatted transfer string.

        :returns: "{name}.{index}"
        """
        s = ''
        if self.name is not '': s += f'{self.name}.'
        s += f'{self.index}'
        return s


from databay import Inlet
from databay import Outlet

_ITERABLE_EXCEPTION = "is not iterable"

class Link():
    """
    Link in the relationship graph. Use this class to define relationships between inlets and outlets.
    """

    def __init__(self, 
                 inlets: Union[Inlet, List[Inlet]],
                 outlets: Union[Outlet, List[Outlet]], 
                 interval:datetime.timedelta, 
                 name:str='',
                 copy_records:bool=True,
                 catch_exceptions:bool=False):
        """
        :type inlets: :any:`Inlet` or list[:any:`Inlet`]
        :param inlets: inlets to add to this link

        :type outlets: :any:`Outlet` or list[:any:`Outlet`]
        :param outlets: outlets to add to this link

        :type interval: datetime.timedelta
        :param interval: Frequency at which this link should transfer.

        :type name: str
        :param name: Human readable identifier of this link |default| :code:`''`

        :type copy_records: bool
        :param copy_records: Whether to copy records before passing them to outlets. |default| :code:`True`

        :type catch_exceptions: bool
        :param catch_exceptions: Whether exceptions in inlets and outlets should be caught or let through. |default| :code:`True`
        """

        self._inlets = []
        self._outlets = []
        self.add_inlets(inlets)
        self.add_outlets(outlets)
        self._interval = interval
        self._count = -1
        self._job = None
        self._name = name
        self._copy_records = copy_records
        self._catch_exceptions = catch_exceptions

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
            assert isinstance(inl, Inlet)
            
            if inl in self._inlets:
                raise InvalidNodeError('Link already contains inlet: %s' % (inl))

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
                raise InvalidNodeError('Link does not contain inlet: %s' % (inl))
             
            self._inlets.remove(inl)

    @property
    def outlets(self) -> List[Outlet]:
        """
        Outlets handled by this link.

        :returns: list[:any:`Outlet`]
        """
        return self._outlets

    def add_outlets(self, outlets:Union[Outlet, List[Outlet]]):
        """
        Add outlets to this link. Outlets must be of type Outlet and not currently added to this link.

        :type outlets: :any:`Outlet` or list[:any:`Outlet`]
        :param outlets: outlets to add to this link

        :raises: :any:`InvalidNodeError` if this link already contains any of the outlets being added.
        """
        if not isinstance(outlets, list):
            outlets = [outlets]

        for outl in outlets:
            assert isinstance(outl, Outlet)

            if outl in self._outlets:
                raise InvalidNodeError('Link already contains outlet: %s' % (outl))

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
                raise InvalidNodeError('Link does not contain outlet: %s' % (outl))

            self._outlets.remove(outl)

    @property
    def interval(self) -> datetime.timedelta:
        """
        Frequency at which this link should transfer.

        :returns: interval object
        :rtype: :class:`datetime.timedelta`
        """
        return self._interval

    def set_job(self, job): # pragma: no cover
        """
        :type job: Any
        :param job: specify the job this link is executed with.
        """
        self._job = job

    @property
    def job(self) -> Any: # pragma: no cover
        """
        The job this link is executed with. Job should persist between link updates.
        |default| :code:`None`

        :returns: Job this link is executed with.
        """
        return self._job

    @property
    def name(self) -> str:
        """
        The human readable identifier of this link. |default| :code:`''`

        :returns: Name of this link
        :rtype: str
        """
        return self._name

    def transfer(self):
        """
        Execute one transfer on this link. This will run through all inlets querying them for data, then pass that data to all outlets.
        """
        asyncio.run(self._run())

    async def _run(self):
        """
        Coroutine handling the transfer.
        """

        self._count += 1
        count = self._count
        update = Update(name=self.name, index=count)
        # print(count, 'transfer')
        _LOGGER.debug(f'{update} transfer')

        async def inlet_task(inlet):
            try:
                return await inlet._pull(update)
            except Exception as e:
                if self._catch_exceptions:
                    _LOGGER.exception(f'Inlet exception: "{e}" for inlet: {inlet}, in: {self}, during: {update}', exc_info=True)
                    return []
                else:
                    raise e

        inlet_tasks = [inlet_task(inlet) for inlet in self._inlets]
        results_raw = await asyncio.gather(*inlet_tasks)
        # print(results_raw)

        # records = []
        # def add_to_records(records, results):
        #     try:
        #         records += results
        #     except Exception as e:
        #         if _ITERABLE_EXCEPTION in str(e):
        #             records = add_to_records(records, [results])
        #         else:
        #             if self._catch_exceptions:
        #                 _LOGGER.exception(f'Unknown Inlet results exception: "{e}" for results: {results}, in link: {self}, during: {update}', exc_info=True)
        #             else:
        #                 raise e
        #
        #     return records
        #
        #
        # for results in results_raw:
        #     records = add_to_records(records, results)
                # iterable_message = f'Inlets must return iterable, found: {results}, in link: {self}, during: {update}'
                #
                # if not self._catch_exceptions:
                #     if _ITERABLE_EXCEPTION in str(e): # format the common iterable error for readability
                #         raise TypeError(iterable_message)
                #     else:
                #         raise e
                #
                # elif _ITERABLE_EXCEPTION in str(e):
                #     _LOGGER.exception(iterable_message, exc_info=False)
                # else:
                #     _LOGGER.exception(f'Unknown Inlet results exception: "{e}" for results: {results}, in link: {self}, during: {update}', exc_info=True)

        records = list(itertools.chain.from_iterable(results_raw))


        async def outlet_task(outlet, records_copy):
            # asyncio.run_coroutine_threadsafe(outlet.push(records), asyncio.get_event_loop())
            try:
                await outlet._push(records_copy, update)
            except Exception as e:
                if self._catch_exceptions:
                    _LOGGER.exception(f'Outlet exception: "{e}" for outlet: {outlet}, in link: {self}, during: {update}', exc_info=True)
                else:
                    raise e

        outlet_tasks = []
        for outlet in self._outlets:
            if self._copy_records:
                task = outlet_task(outlet, copy.deepcopy(records))
            else:
                task = outlet_task(outlet, records)
            outlet_tasks.append(task)
        # outlet_tasks = [outlet_task(outlet, copy.deepcopy(records)) for outlet in self._outlets]
        await asyncio.gather(*outlet_tasks)

        _LOGGER.debug(f'{update} done')



    def on_start(self):
        """
        Called when governing planner is about to start.
        Calls :any:`try_start <Inlet.try_start>` on all inlets and outlets of this link.

        If an inlet or outlet is present in multiple links its on_start will only be called
        once by whichever link executes first.
        """
        for inlet in self._inlets:
            inlet.try_start()

        for outlet in self._outlets:
            outlet.try_start()

    def on_shutdown(self):
        """
        Called just after governing planner has shutdown.
        Calls :any:`try_shutdown <Inlet.try_shutdown>` on all inlets and outlets of this link.

        If an inlet or outlet is present in multiple links its on_shutdown will only be called
        once by whichever link executes first.
        """
        for inlet in self._inlets:
            inlet.try_shutdown()

        for outlet in self._outlets:
            outlet.try_shutdown()

    def __repr__(self):
        """
        :returns: Link(name:%s, inlets:%s, outlets:%s, interval:%s)
        """

        return 'Link(name:%s, inlets:%s, outlets:%s, interval:%s)' % (self.name, self.inlets, self.outlets, self.interval)