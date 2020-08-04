Basic metadata
------------

.. container:: tutorial-block

    This example demonstrates basic usage of :ref:`Global metadata <global_metadata>`, used by a PrintOutlet created in the :ref:`Basic Outlet <basic_metadata>` example.

    #. Create the :code:`ConditionalPrintOutlet` implementing :any:`Outlet` class. This outlet will accept one metadata key:

        * :code:`ConditionalPrintOutlet.SHOULD_PRINT` - whether record should be printed.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :lines: 9-12

    #. Implement :code:`push` method, looping over all records and printing them if :code:`ConditionalPrintOutlet.SHOULD_PRINT` is set:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :lines: 14-17

    #. Instantiate two inlets, one that always prints, other that never prints:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :lines: 20-21

    #. Instantiate :code:`ConditionalPrintOutlet` and add all nodes to a link

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :lines: 23-28

    Full example:

    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python

    Produces:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> should_print_metadata.0 Record(payload=44, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
        >>> should_print_metadata.1 Record(payload=14, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
        >>> should_print_metadata.2 Record(payload=54, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
        >>> ...