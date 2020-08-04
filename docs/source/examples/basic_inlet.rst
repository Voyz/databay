Basic Inlet
------------

.. container:: tutorial-block

    In this example we create a simple implementation of :any:`Inlet`, producing a random integer on a 5 second interval.

    #. Extend the :any:`Inlet` class, returning produced data from the :any:`pull` method:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python
        :lines: 8-11

    #. Instantiate it:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python
        :lines: 14

    #. Add it to a link:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python
        :lines: 18-21

    Full code:

    .. literalinclude:: ../../examples/basic_inlet.py
        :language: python

    Produces:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> random_ints.0 50
        >>> random_ints.1 61
        >>> random_ints.2 5
        >>> ...