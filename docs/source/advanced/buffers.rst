.. _buffers:

Buffers
=======

.. contents::
    :local:
    :backlinks: entry

:any:`Buffers <Buffer>` are special built-in :any:`processors`. They allow you to temporarily accumulate records before passing them over to outlets.


Simple example
--------------

.. container:: tutorial-block

    The following example uses a buffer to store the records until the number of records produced exceed 10 items.

    #. Define a buffer with :code:`count_threshold=10`:

    .. code-block:: python

        buffer = Buffer(count_threshold=10)
        link = Link(inlet, outlet, processors=buffer)

    #. On first transfer the inlet produces 4 records, the buffer stores them. The outlet receives no records.
    #. On second transfer the inlet produces 4 records, the buffer stores them along with the first 4. The outlet still receives no records.
    #. On third transfer the inlet produces 3 records. Having exceeded the count_threshold of :code:`10`, the buffer will release all 11 records to the outlet. The outlet receives a list of 11 records.


Store or release?
-----------------

When processing records (see :any:`processors`) a :any:`Buffer` will figure out whether records should be stored or released. This is done by passing the list of records to :any:`Buffer's <Buffer>` internal :any:`callable` functions called controllers.

Each controller performs different types of checks, returning :code:`True` or :code:`False` depending on whether records should be released or stored respectively.



Default controllers
-------------------

:any:`Buffer` comes with two default controllers:

* :code:`count_controller` - buffering records until reaching a count threshold defined by :code:`Buffer.count_threshold` parameter, counted from the first time the records are stored. For example:

.. code-block:: python

    buffer = Buffer(count_threshold=50) # release records every 50 records.

* :code:`time_controller` - buffering records until reaching a time threshold defined by :code:`Buffer.time_threshold` parameter, counted from the first time the records are stored. For example:

.. code-block:: python

    buffer = Buffer(time=60) # release records every 60 seconds.

Custom controllers
------------------

Apart from using the default controllers, buffer accepts any number of custom controllers. Each controller will be called with the list of records and is expected to return :code:`True` or :code:`False` depending on whether records should be buffered or released. For example:

.. code-block:: python

    def big_value_controller(records: List[Records]):
        for record in records:
            if record.payload.value > 10000
                return True

        return False

    buffer = Buffer(custom_controllers=big_value_controller)

.. _buffer-reset:

Buffer reset
------------

Every time the records are released, the buffer will reset the counters of its default controllers and empty the list of records stored.

Combining controllers
---------------------

You can use any combination of default and custom controllers. The buffer will release the records if any controller returns :code:`True` (ie. boolean :code:`OR`).

.. code-block:: python

    buffer = Buffer(count_threshold=10, time_threshold=60)

This buffer will release records once 10 records were produced or 60 seconds have elapsed - whichever comes first.

Once any controller returns :code:`True`, the :any:`buffer will reset<buffer-reset>`.

Flush
-------------

:any:`Buffer` contains a boolean field called :code:`flush`, which if set to :code:`True` will enforce release of records, independently of what the controllers may decide. Such flushing will only take place next time the buffer is called during the upcoming transfer. Flushing will also :any:`reset the buffer<buffer-reset>`.

Best practices
--------------

.. rubric:: One-to-one relationship

Given the internal record storage functionality, one buffer should only be used as either :any:`a Link or an Outlet processor <link-outlet-processors>` - but never both at the same time.

Similarly, one buffer should only be used on one :any:`Link` or :any:`Outlet` - never multiple at the same time.

.. rubric:: Ensure records are consumed

Note that in several scenarios a buffer may never release its records, therefore they would never be consumed by the outlets. Consider the following examples:

* Databay crashes before records are released.
* Planner is stopped before records are released.
* Thresholds are set to unreachable numbers

Databay does not automatically handle such occasions, however you may expect these and ensure that records are released manually by combining the buffer's :any:`flush` functionality with planners' :any:`force_transfer` method.

.. code-block:: python

    try:
        # set up Databay
        buffer = Buffer(count_threshold=4000)
        link = Link(inlets, outlets, interval=10)
        planner = SchedulePlanner(link)
        planner.start()

    except Exception as e:
        print('Error while running Databay: ' + str(e))

    finally:
        buffer.flush = True # ensure the buffer will release data
        link.remove_inlets(link.inlets) # we don't need to produce any more data
        planner.force_transfer() # run one final transfer to flush the data
