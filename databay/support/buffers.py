import logging
import time
from typing import List, Union

from databay import Record

_LOGGER = logging.getLogger('databay.Buffer')

class Buffer():
    """
    Buffers are special built-in :any:`processors`. They allow you to temporarily accumulate records before passing them over to outlets.

    When processing records (see :any:`processors`) a Buffer will figure out whether records should be stored or released. This is done by passing the list of records to Buffer's internal :any:`callable` functions called controllers.

    Each controller performs different types of checks, returning :code:`True` or :code:`False` depending on whether records should be released or stored respectively.
    """

    def __init__(self,
                 count_threshold : int = None,
                 time_threshold: float = None,
                 custom_controllers: Union[callable, List[callable]] = None,
                 on_reset: callable = None,
                 controller_conjunction: bool = False
                 ):
        """

        :type count_threshold: int
        :param count_threshold: The number of records stored that when reached will complete the count controller. When set to :code:`None` it will disable the count controller.
            |default| :code:`None`

        :type time_threshold: float
        :param time_threshold: The number of seconds elapsed since the previous release that when reached will complete the time controller. When set to :code:`None` it will disable the time controller.
            |default| :code:`None`

        :type custom_controllers: :any:`callable` or list[:any:`callable`]
        :param custom_controllers: List of custom :any:`callable` controllers.
            |default| :code:`None`

        :type on_reset: :any:`callable`
        :param on_reset: Callback invoked when :any:`reset <Buffer.reset>` is called.
            |default| :code:`None`

        :type controller_conjunction: bool
        :param controller_conjunction: Whether to release the records when any controller returns :code:`True` or to wait for all of them to complete before releasing records.
            |default| :code:`False`

        """

        self.count_threshold = count_threshold
        self.time_threshold = time_threshold
        self.custom_controllers = custom_controllers
        self.controller_conjunction = controller_conjunction

        if self.custom_controllers is None:
            self.custom_controllers = []
        elif not isinstance(self.custom_controllers, list):
            self.custom_controllers : List[callable] = [self.custom_controllers]


        self.controllers = []
        self.records = []

        self.time_start = None
        self.flush = False

        self.on_reset = on_reset


    def _count_controller(self, records:List[Record]) -> bool:
        if len(records) > self.count_threshold:
            return True
        else:
            return False

    def _time_controller(self, records:List[Record]) -> bool:
        if self.time_start is None:
            self.time_start = time.time()

        if time.time() > (self.time_start + self.time_threshold):
            return True
        else:
            return False

    def get_controllers(self):
        """
        Return the list of currently active controllers.

        :returns: list of controllers
        :rtype: list[:any:`callable`]
        """
        controllers = []
        controllers = controllers + self.custom_controllers
        if self.count_threshold is not None:
            controllers.append(self._count_controller)
        if self.time_threshold is not None:
            controllers.append(self._time_controller)
        return controllers


    def _execute(self, records:List[Record]) -> List[Record]:
        self.records += records
        rv = []
        if self.flush:
            rv =  self.records
        else:
            if self.controller_conjunction:
                controllers_passing = True
                for controller in self.get_controllers():
                    try:
                        controllers_passing &= controller(self.records)
                    except Exception as e:
                        _LOGGER.exception(f'Exception while running controller {controller} with records {records}. Content: {str(e)}')
                        continue

                    if not controllers_passing:
                        break # one controller returned False, skip the rest
                if controllers_passing:
                    rv = self.records
            else:
                for controller in self.get_controllers():
                    try:
                        decision = controller(self.records)
                    except Exception as e:
                        _LOGGER.exception(f'Exception while running controller {controller} with records {records}. Content: {str(e)}')
                        continue

                    if decision:
                        rv = self.records
                        break # one controller returned True, skip the rest

        if rv != []:
            self.reset()
        return rv


    def __call__(self, records:List[Record]):
        return self._execute(records)

    def reset(self):
        """
        Resets this buffer, resetting the controllers' counters and emptying the list of records stored.
        """
        self.records = []
        self.time_start = None
        self.flush = False

        if self.on_reset is not None:
            self.on_reset()