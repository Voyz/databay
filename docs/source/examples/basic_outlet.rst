Basic Outlet
------------

.. container:: tutorial-block

    In this example we create a simple implementation of :any:`Outlet`, printing the incoming records one by one.

    #. Extend the :any:`Outlet` class, printing the incoming data in the :any:`push` method:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_outlet.py
        :language: python
        :lines: 9-13

    #. Instantiate it:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_outlet.py
        :language: python
        :lines: 17

    #. Add it to a link:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_outlet.py
        :language: python
        :lines: 19-22

    Full example:

    .. literalinclude:: ../../examples/basic_outlet.py
        :language: python

    Produces:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> print_outlet.0 10
        >>> print_outlet.1 34
        >>> print_outlet.2 18
        >>> ...