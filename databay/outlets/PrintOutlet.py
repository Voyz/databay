from databay.outlet import Outlet
from databay.record import Record


class PrintOutlet(Outlet):

    async def push(self, records:[Record], count):
        for record in records:
            print(count, record)
