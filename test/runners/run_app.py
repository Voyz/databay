import logging
import time
from datetime import timedelta
from threading import Thread

from databay import Link
from databay.planners import APSPlanner, SchedulePlanner
# from databay.inlets.AlphavantageInlet import AlphavantageInlet
from databay.inlets import HttpInlet
from databay.outlets import CsvOutlet
from databay.outlets import MongoOutlet
from databay.outlets import PrintOutlet

logging.getLogger('databay').setLevel(logging.DEBUG)

class Run_App():
    def __init__(self,):
        pass

    def run(self):
        # planner = APSPlanner()
        planner = SchedulePlanner(refresh_interval=0.5)

        # alphavantage_inlet = AlphavantageInlet(key='9TZBJ8V9EMEES2WN', symbol='TSLA', interval='1min', metadata={'mongodb_collection': 'alpha_prices'})
        http_inlet = HttpInlet('https://jsonplaceholder.typicode.com/todos/1')
        http_inlet2 = HttpInlet('https://postman-echo.com/get?foo1=bar1&foo2=bar2', metadata={'mongodb_collection': 'test_collection2', 'csv_file': 'output_02.csv'})

        print_outlet = PrintOutlet()
        mongo_outlet = MongoOutlet('databay', 'test_collection')
        csv_outlet = CsvOutlet('output_01.csv')

        # planner.add_link(Link([http_inlet2, http_inlet2, http_inlet2, http_inlet], [csv_outlet], timedelta(seconds=2)))
        planner.add_link(Link([http_inlet], [mongo_outlet], timedelta(seconds=1), name='first'))
        planner.add_link(Link([http_inlet2, http_inlet2, http_inlet2], [mongo_outlet], timedelta(seconds=5), name='second'))
        planner.add_link(Link([], [], timedelta(seconds=1.5)))
        # planner.add_link(Link([alphavantage_inlet], [mongo_outlet], timedelta(seconds=5)))
        # planner.add_link(Link([iex_inlet], [mongo_outlet], timedelta(seconds=5)))
        planner.start()

        # th = Thread(target=planner.start)
        # th.start()

        # asyncio.get_event_loop().run_forever()
        # while True:
        #     print('aAA!')
        #     time.sleep(1)


if __name__ == '__main__':
    Run_App().run()