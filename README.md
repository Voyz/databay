*This library is currently being beta-tested. See something that's broken? Did we get something wrong? [Create an issue and let us know!][issues]*

<h1 align="center" name="databay">
    <img src="/databay_title.png" alt="Databay title" title="Databay title" width="600"/>

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![GitHub Release](https://img.shields.io/pypi/v/databay?label=version)]()
    
</h1>


          


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

* **Simple, decoupled interface** — Easily implement [data production][extending_inlets] and [consumption][extending_outlets] that fits your needs.

* **Granular control over data transfer** — Multiple ways of [passing information][records] between producers and consumers.

* **[Asyncio][asyncio] supported** — You can [produce][async_inlet] or [consume][async_outlet] asynchronously.

* **We'll handle the rest** — [scheduling][scheduling], [startup and shutdown][startup_and_shutdown], [exception handling][exceptions], [logging][logging].

* **Support for custom scheduling** — Use [your own scheduling logic][extending_base_planner] if you like.


  
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

## <a name="community"></a>Community Contributions

We aim to support the ecosystem of Databay users by collating and promoting inlets and outlets that implement popular functionalities. We encourage you to share the inlets and outlets you write with the community - start by reading the [guidelines][community_docs] on contributing to the Databay community.

Did you write a cool inlet or outlet that you'd like to share with others? Put it on a public repo, send us an [email][voy1982_email] and we'll list it here!

[voy1982@yahoo.co.uk][voy1982_email]

#### Inlets

* [FileInlet](https://databay.readthedocs.io/en/latest/api/databay/inlets/file_inlet/index.html) - File input inlet (built-in).
* [HttpInlet](https://databay.readthedocs.io/en/latest/api/databay/inlets/http_inlet/index.html) - Asynchronous http request inlet using aiohttp (built-in).

#### Outlets

* [FileOutlet](https://databay.readthedocs.io/en/latest/api/databay/outlets/file_outlet/index.html) - Generic file outlet (built-in).
* [CsvOutlet](https://databay.readthedocs.io/en/latest/api/databay/outlets/csv_outlet/index.html) - CSV file outlet (built-in).
* [MongoOutlet](https://databay.readthedocs.io/en/latest/api/databay/outlets/mongo_outlet/index.html) - MongoDB outlet (built-in).


## <a name="roadmap"></a>Roadmap

#### v1.0
1. Beta test the pre-release.
1. Complete 100% test coverage (currently 75%).
1. Add more advanced examples.
1. Release v1.0.
1. Buy a carrot cake and celebrate.

#### v1.1
1. Filters and translators - callbacks for processing data between inlets and outlets.
1. Advanced scheduling - conditional, non uniform intervals.


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
  [startup_and_shutdown]: https://databay.readthedocs.io/en/latest/introduction.html#start-and-shutdown
  [async_inlet]: https://databay.readthedocs.io/en/latest/extending/extending_inlets.html#asynchronous-inlet
  [async_outlet]: https://databay.readthedocs.io/en/latest/extending/extending_outlets.html#asynchronous-outlet
  [voy1982_email]: mailto:voy1982@yahoo.co.uk
  [issues]: https://github.com/Voyz/databay/issues
  [community_docs]: https://databay.readthedocs.io/en/latest/extending/community_contributions.html