"""
.. seealso::

    * :ref:`Extending Inlets <extending_inlets>` to learn how to extend this class correctly.
    * :any:`Outlet` representing the corresponding output of the data stream.
"""

import asyncio
import threading
from abc import ABC, abstractmethod
from typing import List

from databay import Record
import databay as da




class Inlet(ABC):
    """
    Abstract class representing an input of the data stream.
    """

    def __init__(self, metadata:dict=None):
        """
        :type metadata: dict
        :param metadata: Global metadata that will be attached to each record generated by this inlet. It can be overridden or appended to by providing metadata when creating a record using :py:func:`new_record` function. |default| :code:`None`
        """
        self._metadata = metadata if metadata is not None else {}

        self._active = False

        self._uses_coroutine = asyncio.iscoroutinefunction(self.pull)
        self._thread_lock = threading.Lock()

    @property
    def metadata(self):
        """
        Global metadata that will be attached to each record generated by this inlet.
        It can be overridden or appended to by providing metadata when creating a
        record using :py:func:`new_record` function.

        :returns: Metadata dictionary.
        :rtype: dict
        """
        return self._metadata

    async def _pull(self, update:'da.Update'):
        if self._uses_coroutine:
            data = await self.pull(update)
        else:
            data = self.pull(update)

        if not isinstance(data, list):
            data = [data]

        if data and not isinstance(data[0], Record):
            for i in range(len(data)):
                entry = data[i]
                if not isinstance(entry, Record):
                    data[i] = self.new_record(payload=entry)

        return data


    @abstractmethod
    def pull(self, update:'da.Update') -> List[Record]:
        """
        Produce new data.

        Override this method to define how this inlet will produce new data.

        :type update: :any:`Update`
        :param update: Update object representing the particular Link update run.

        :return: List of records produced
        :rtype: list[:any:`Record`]

        """
        raise NotImplementedError()

    def new_record(self, payload, metadata:dict=None) -> Record:
        """
        Create a new :any:`Record`. This should be the preferred way of creating new records.

        :type payload: Any
        :param payload: Data produced by this inlet.

        :type metadata: dict
        :param metadata: Local metadata that will override and/or append to the global metadata. It will be attached to the new record.
            |default| :code:`None`

        :returns: New record created
        :rtype: :any:`Record`
        """

        full_metadata = {**self._metadata, **(metadata if metadata is not None else {})}
        full_metadata['__inlet__'] = str(self)
        return Record(payload=payload, metadata=full_metadata)

    def try_start(self):
        """
        Wrapper around on_start call that will ensure it only gets executed once.
        """

        should_on_start = False

        with self._thread_lock:
            if not self._active:
                #
                self._active = True
                should_on_start = True

        if should_on_start:
            self.on_start()

    def on_start(self):
        """
        Called once per inlet just before the governing planner is about to start.

        Override this method to provide starting functionality on this inlet.
        """
        pass

    def try_shutdown(self):
        """
        Wrapper around on_shutdown call that will ensure it only gets executed once.
        """

        should_on_shutdown = False

        with self._thread_lock:
            if self._active:
                self._active = False
                should_on_shutdown = True

        if should_on_shutdown:
            self.on_shutdown()

    def on_shutdown(self):
        """
        Called once per inlet just after the governing planner has shutdown.

        Override this method to provide shutdown functionality on this inlet.
        """
        pass

    @property
    def active(self):
        """
        Whether this inlet is active and ready to pull. This variable is set by
        the governing link to :code:`True` on start and to :code:`False` on shutdown.
        |default| :code:`False`

        :rtype: bool
        """
        return self._active


    def __repr__(self):
        s = "%s(" % (self.__class__.__name__)

        if self.metadata:
            s += 'metadata=%s' % self.metadata

        s += ')'

        return s