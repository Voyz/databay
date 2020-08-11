Basic asynchronous
------------

.. container:: tutorial-block

    This tutorial showcases a simple usage of asynchronous inlets and outlets.

    #. Create an asynchronous inlet.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_asynchronous.py
        :language: python
        :start-at: class RandomIntInlet
        :end-at: return r

    #. Create an asynchronous outlet. Note that one asynchronous wait will be simulated for each record consumed.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_asynchronous.py
        :language: python
        :start-at: class PrintOutlet
        :end-at: _LOGGER.debug(f'{update} consumed:

    #. Instantiate three asynchronous inlets and one asynchronous outlet.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_asynchronous.py
        :language: python
        :start-at: random_int_inletA =
        :end-at: name='async'

    #. Add to a planner and schedule.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_asynchronous.py
        :language: python
        :start-at: planner =
        :end-at: planner.start

    Output:

    .. rst-class:: highlight-small
    .. code-block:: python

            >>> 2020-08-04 22:40:41.242|D| async.0 transfer
            >>> 2020-08-04 22:40:41.754|D| async.0 produced:20
            >>> 2020-08-04 22:40:41.754|D| async.0 produced:55
            >>> 2020-08-04 22:40:41.754|D| async.0 produced:22
            >>> 2020-08-04 22:40:41.755|D| async.0 push starts
            >>> 2020-08-04 22:40:42.267|D| async.0 consumed:20
            >>> 2020-08-04 22:40:42.267|D| async.0 consumed:55
            >>> 2020-08-04 22:40:42.267|D| async.0 consumed:22
            >>> 2020-08-04 22:40:42.267|D| async.0 done

            >>> 2020-08-04 22:40:43.263|D| async.1 transfer
            >>> 2020-08-04 22:40:43.776|D| async.1 produced:10
            >>> 2020-08-04 22:40:43.776|D| async.1 produced:4
            >>> 2020-08-04 22:40:43.776|D| async.1 produced:90
            >>> 2020-08-04 22:40:43.777|D| async.1 push starts
            >>> 2020-08-04 22:40:44.292|D| async.1 consumed:10
            >>> 2020-08-04 22:40:44.292|D| async.1 consumed:4
            >>> 2020-08-04 22:40:44.292|D| async.1 consumed:90
            >>> 2020-08-04 22:40:44.292|D| async.1 done

    On each transfer, two asynchronous operations take place:

        * First, all inlets are simultaneously awaiting before producing their data.
        * Once all data from inlets is gathered, the second stage commences where the outlet simultaneously awaits for each record before printing it out.

    This simulates a delay happening either in the inlets or outlets. Note how one transfer takes approximately a second to complete, despite executing six operations each requiring 0.5 seconds of sleep. If this was to execute synchronously, the entire transfer would take around 3 seconds to complete.

    Full example:

    .. literalinclude:: ../../examples/basic_asynchronous.py
        :language: python

