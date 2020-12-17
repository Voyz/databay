import asyncio
import logging

from databay import Link, Outlet, Record
from databay.planners import SchedulePlanner
from datetime import timedelta
from databay import Inlet
import random

_LOGGER = logging.getLogger('databay.basic_asynchronous')
logging.getLogger('databay').setLevel(logging.DEBUG)


class RandomIntInlet(Inlet):

    async def pull(self, update):

        # simulate a long-taking operation
        await asyncio.sleep(0.5)

        # execute
        r = random.randint(0, 100)

        _LOGGER.debug(f'{update} produced:{r}')
        return r


class PrintOutlet(Outlet):

    async def push(self, records: [Record], update):
        _LOGGER.debug(f'{update} push starts')

        # create an asynchronous task for each record
        tasks = [self.print_task(record, update) for record in records]

        # await all print tasks
        await asyncio.gather(*tasks)

    async def print_task(self, record, update):

        # simulate a long-taking operation
        await asyncio.sleep(0.5)

        # execute
        _LOGGER.debug(f'{update} consumed:{record.payload}')


random_int_inletA = RandomIntInlet()
random_int_inletB = RandomIntInlet()
random_int_inletC = RandomIntInlet()
print_outlet = PrintOutlet()

link = Link([random_int_inletA, random_int_inletB, random_int_inletC],
            print_outlet,
            interval=timedelta(seconds=2),
            tags='async')

planner = SchedulePlanner(link)
planner.start()
