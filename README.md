# Databay [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
          


Databay is a Python interface for **scheduled data transfer**. It facilitates transfer of (any) data from A to B, on a scheduled interval.

## Installation

```python
pip install databay
```

## Documentation

See full **[Databay documentation][docs]**.

Or more specifically:

* [Overview][overview] - Learn what is Databay.
* [Examples][examples] - See Databay in use.
* [Extending Databay][extending] - Use Databay in your project.
* [API Reference][api] - Read the API documentation.


## Features

* **Simple, decoupled interface** - Easily implement [data production][extending_inlets] and [consumption][extending_outlets] that fits your needs.

* **Granular control over data transfer** - Multiple ways of [passing information][records] between producers and consumers.
    
* **Asynchronous execution** - [asyncio][asyncio] supported.

* **We'll handle the rest** - [scheduling][scheduling], [exception handling][exceptions], [logging][logging], job management.

* **Support for custom scheduling** - Use your own scheduling logic [if you like][extending_base_planner].


  
## Overview

In Databay, data transfer is expressed with three components:

* `Inlets` - for data production.
* `Outlets` - for data consumption.
* `Links` - for handling the data transit between inlets and outlets.

Scheduling is implemented using third party libraries, exposed through the `BasePlanner` interface. Currently two `BasePlanner` implementations are available - using [Advanced Python Scheduler][aps] and [Schedule][schedule].

[A simple example][simple_example]:

```python
# Data producer
inlet = HttpInlet('https://some.test.url.com/')

# Data consumer
outlet = MongoOutlet('databay', 'test_collection')

# Data transfer between the two
link = Link(inlet, outlet, datetime.timedelta(seconds=5))

# Start scheduling
planner = APSPlanner(link)
planner.start()
```

Every 5 seconds this snippet will pull data from a test URL, and write it to MongoDB.

---- 

While Databay comes with a handful of built-in inlets and outlets, its strength lies in extendability. To use Databay in your project, create concrete implementations of `Inlet` and `Outlet` classes that handle the data production and consumption functionality you require. Databay will then make sure data can repeatedly flow between the inlets and outlets you create. [Extending inlets][extending_inlets] and [extending outlets][extending_outlets] is easy and has a wide range of customization. Head over to [Extending Databay][extending] section for a detailed explanation or to [Examples][examples] for real use cases. 

## Licence

See [LICENSE](LICENSE)


  [docs]: https://databay.readthedocs.io/
  [overview]: https://databay.readthedocs.io/en/latest/introduction.html#overview
  [examples]: https://databay.readthedocs.io/en/latest/examples.html
  [api]: https://databay.readthedocs.io/en/latest/api/databay/index.html
  [aps]: http://apscheduler.readthedocs.io/
  [schedule]: https://schedule.readthedocs.io/
  [simple_example]: https://databay.readthedocs.io/en/latest/examples.html#simple-usage
  [extending]: https://databay.readthedocs.io/en/latest/extending.html
  [extending_inlets]: https://databay.readthedocs.io/en/latest/extending/extending_inlets.html
  [extending_outlets]: https://databay.readthedocs.io/en/latest/extending/extending_outlets.html
  [asyncio]: https://docs.python.org/3/library/asyncio.html
  [records]: https://databay.readthedocs.io/en/latest/introduction.html#records
  [scheduling]: https://databay.readthedocs.io/en/latest/introduction.html#scheduling
  [exceptions]: https://databay.readthedocs.io/en/latest/introduction.html#exception-handling
  [logging]: https://databay.readthedocs.io/en/latest/introduction.html#logging
  [extending_base_planner]: https://databay.readthedocs.io/en/latest/extending/extending_base_planner.html