import random
from datetime import timedelta

from databay import Link, Inlet
from databay.outlet import Outlet
from databay.planners import SchedulePlanner
from databay.record import Record


class RandomIntInlet(Inlet):

    def pull(self, update):
        return random.randint(0, 100)


class PrintOutlet(Outlet):
    SHOULD_PRINT = 'PrintOutlet.SHOULD_PRINT'

    async def push(self, records:[Record], update):
        for record in records:
            if record.metadata.get(self.SHOULD_PRINT):
                print(update, record)


random_int_inlet_on = RandomIntInlet(metadata={PrintOutlet.SHOULD_PRINT: True})
random_int_inlet_off = RandomIntInlet(metadata={PrintOutlet.SHOULD_PRINT: False})

print_outlet = PrintOutlet()

link = Link([random_int_inlet_on, random_int_inlet_off],
            print_outlet,
            interval=timedelta(seconds=0.5),
            name='should_print_metadata')

planner = SchedulePlanner(refresh_interval=0.5)
planner.add_link(link)
planner.start()