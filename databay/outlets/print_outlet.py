from databay.outlet import Outlet
from databay.record import Record


class PrintOutlet(Outlet):

    def __init__(self, only_payload:bool=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.only_payload = only_payload

    async def push(self, records:[Record], update):
        for record in records:
            if self.only_payload:
                print(update, record.payload)
            else:
                print(update, record)