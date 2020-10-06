import logging
import time
from datetime import timedelta
from threading import Thread

from databay import Link
from databay.inlets.file_inlet import FileInlet, FileInletMode
from databay.planners import APSPlanner, SchedulePlanner
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


        http_inlet = HttpInlet('https://jsonplaceholder.typicode.com/todos/1', metadata={CsvOutlet.FILE_MODE:'a'})
        file_inlet = FileInlet('output_03.csv', read_mode=FileInletMode.LINE)
        http_inlet2 = HttpInlet('https://postman-echo.com/get?foo1=bar1&foo2=bar2', metadata={'MONGODB_COLLECTION': 'test_collection2', 'csv_file': 'output_02.csv'})

        print_outlet = PrintOutlet(only_payload=True)
        mongo_outlet = MongoOutlet('databay', 'test_collection')
        csv_outlet = CsvOutlet('output_03.csv')

        planner.add_links(Link([file_inlet], [print_outlet], timedelta(seconds=0.5)))
        planner.add_links(Link([http_inlet, http_inlet, http_inlet], [csv_outlet], timedelta(seconds=2)))
        # planner.add_links(Link([http_inlet], [mongo_outlet], timedelta(seconds=1), tags='first'))
        # planner.add_links(Link([http_inlet2, http_inlet2, http_inlet2], [mongo_outlet], timedelta(seconds=5), tags='second'))
        # planner.add_links(Link([], [], timedelta(seconds=1.5)))
        # planner.add_links(Link([alphavantage_inlet], [mongo_outlet], timedelta(seconds=5)))
        # planner.add_links(Link([iex_inlet], [mongo_outlet], timedelta(seconds=5)))
        planner.start()

        # th = Thread(target=planner.start)
        # th.start()

        # asyncio.get_event_loop().run_forever()
        # while True:
        #     print('aAA!')
        #     time.sleep(1)


if __name__ == '__main__':
    Run_App().run()