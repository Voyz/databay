# pragma: no cover

from datetime import timedelta

from databay import Link
from databay.inlets import HttpInlet
from databay.outlets import MongoOutlet

# logging.getLogger('databay').setLevel(logging.INFO)
from databay.planners import APSPlanner, SchedulePlanner


def run():
    # planner = SchedulePlanner(multithreaded=True, refresh_interval=0.5)
    planner = APSPlanner()

    http_inlet = HttpInlet('https://jsonplaceholder.typicode.com/todos/1')
    mongo_outlet = MongoOutlet('databay', 'test_collection')

    planner.add_link(Link(http_inlet, mongo_outlet, timedelta(seconds=1), name='http_to_mongo'))
    planner.start()


if __name__ == '__main__':
    run()
