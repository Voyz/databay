import datetime

from databay.inlets import HttpInlet
from databay.outlets import PrintOutlet
from databay import Link
from databay.planners import APSPlanner

from databay.outlets.file_outlet import FileOutlet


#filter
class BitcoinInlet(HttpInlet):
    async def pull(self, update):
        response = await super().pull(update)
        return response.get('USD').get('last')

#produce
# stock_inlet = HttpInlet('https://blockchain.info/ticker')
stock_inlet = BitcoinInlet('https://blockchain.info/ticker')

#consume
print_outlet = PrintOutlet(True, True)
file_outlet = FileOutlet('bitcoin_price_1s.txt')

#transfer
link = Link(stock_inlet, [print_outlet, file_outlet],
            interval=datetime.timedelta(seconds=1))

planner = APSPlanner(link)
planner.start()