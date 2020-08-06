from datetime import timedelta

from databay import Link
from databay.inlets import RandomIntInlet
from databay.planners import SchedulePlanner
from databay.record import Record
from databay.outlet import Outlet

class PrintOutlet(Outlet):

    def push(self, records:[Record], update):
        for record in records:
            print(update, record.payload)


random_int_inlet = RandomIntInlet()
print_outlet = PrintOutlet()

link = Link(random_int_inlet,
            print_outlet,
            interval=timedelta(seconds=2),
            name='print_outlet')

planner = SchedulePlanner(link)
planner.start()