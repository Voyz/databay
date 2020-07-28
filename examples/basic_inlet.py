import random

from databay import Inlet, Link
from databay.outlets import PrintOutlet
from databay.planners import SchedulePlanner
from datetime import timedelta

class RandomIntInlet(Inlet):

    def pull(self, update):
        return random.randint(0, 100)


random_int_inlet = RandomIntInlet()

link = Link(random_int_inlet, PrintOutlet(only_payload=True),
            interval=timedelta(seconds=5), name='random_ints')

planner = SchedulePlanner()
planner.add_link(link)
planner.start()