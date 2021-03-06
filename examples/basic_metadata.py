from datetime import timedelta

from databay import Link
from databay.inlets import RandomIntInlet
from databay.outlet import Outlet
from databay.planners import SchedulePlanner
from databay.record import Record


class ConditionalPrintOutlet(Outlet):

    SHOULD_PRINT = 'ConditionalPrintOutlet.SHOULD_PRINT'
    """Whether records should be printed or skipped."""

    def push(self, records: [Record], update):
        for record in records:
            if record.metadata.get(self.SHOULD_PRINT):
                print(update, record)


random_int_inlet_on = RandomIntInlet(
    metadata={ConditionalPrintOutlet.SHOULD_PRINT: True})
random_int_inlet_off = RandomIntInlet(
    metadata={ConditionalPrintOutlet.SHOULD_PRINT: False})

print_outlet = ConditionalPrintOutlet()

link = Link([random_int_inlet_on, random_int_inlet_off],
            print_outlet,
            interval=timedelta(seconds=0.5),
            tags='should_print_metadata')

planner = SchedulePlanner(link, refresh_interval=0.5)
planner.start()
