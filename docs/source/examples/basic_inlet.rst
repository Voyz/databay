Basic Inlet
------------

.. container:: tutorial-block

    In this example we create a simple implementation of :any:`Inlet`, producing a random integer on a 5 second interval.

    #. Extend the :any:`Inlet` class, returning produced data from the :any:`pull <Inlet.pull>` method:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python
        :start-at: class RandomIntInlet
        :end-at: return random

    #. Instantiate it:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python
        :start-at: RandomIntInlet()
        :end-at: RandomIntInlet()

    #. Add it to a link:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python
        :start-at: link = Link
        :end-at: name='random_ints'

    #. Add to a planner and schedule.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python
        :start-at: planner =
        :end-at: planner.start

    Output:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> random_ints.0 50
        >>> random_ints.1 61
        >>> random_ints.2 5
        >>> ...

    On each transfer :code:`RandomIntInlet` produces a random integer.

    Full example:

    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python

