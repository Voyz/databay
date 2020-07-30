Link transfer
-------------

One cycle of data production, propagation and consumption is called *transfer*. During transfer, a link will pull data from all its inlets and then push that collected data to all its outlets.

Each link contains an interval at which it will run the data transfer. This interval is specified on construction with the :code:`interval` parameter of type :any:`datetime.timedelta`.

.. code-block:: python

    Link([inlets], [outlets], interval=datetime.timedelta(minutes=10))

One quantity of data handled by Databay is represented with a :any:`Record`.

.. image:: _static/images/databay_transfer_basic.png

Both pulling and pushing is executed asynchronously, yet pushing only starts once all inlets have finished returning their data.

.. _transfer-update:

.. rubric:: Transfer Update

Each transfer is identified by a unique :any:`Update` object that is available to all inlets and outlets affected by that transfer. It contains the name of the governing link (if specified) and an incremental integer index. Use the :code:`str(update)` to get a formatted string of that update.

.. code-block:: python

    # for link called 'twitter_link' and the 16th transfer execution.
    >>> print(update)
    twitter_link.16