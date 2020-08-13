# Databay [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
          


Databay is a Python interface for **scheduled data transfer**. It facilitates transfer of (any) data from A to B, on a scheduled interval.

### Installation

```python
pip install databay
```

### Documentation

See full **[Databay documentation][1]**.

Or more specifically:

* [Overview][2] - Learn what is Databay.
* [Examples][3] - See Databay in use.
* [Extending Databay][4] - Use Databay in your project.
* [API Reference][5] - Read the API documentation.




  
### Overview

In Databay, data transfer is expressed with three components:

* `Inlets` - for data production.
* `Outlets` - for data consumption.
* `Links` - for handling the data transit between inlets and outlets.

Scheduling is implemented using third party libraries, exposed through the `BasePlanner` interface. Currently two `BasePlanner` implementations are available - using [Advanced Python Scheduler][aps] and [Schedule][schedule].
  
[A simple example][simple_example]:

```python
# Create an inlet, outlet and a link.
http_inlet = HttpInlet('https://some.test.url.com/')
mongo_outlet = MongoOutlet('databay', 'test_collection')
link = Link(http_inlet, mongo_outlet, datetime.timedelta(seconds=5))

# Create a planner, add the link and start scheduling.
planner = APSPlanner(link)
planner.start()
```

Every 5 seconds this snippet will pull data from a test URL, and write it to MongoDB.

### Licence

See [LICENSE](LICENSE)


  [1]: https://databay.readthedocs.io/
  [2]: https://databay.readthedocs.io/en/latest/introduction.html#overview
  [3]: https://databay.readthedocs.io/en/latest/examples.html
  [4]: https://databay.readthedocs.io/en/latest/extending.html
  [5]: https://databay.readthedocs.io/en/latest/api/databay/index.html
  [aps]: http://apscheduler.readthedocs.io/
  [schedule]: https://databay.readthedocs.io/en/latest/api/databay/index.html
  [simple_example]: https://databay.readthedocs.io/en/latest/examples.html#simple-usage