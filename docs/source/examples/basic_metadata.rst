Basic metadata
--------------

.. container:: tutorial-block

    This example demonstrates basic usage of :ref:`Global metadata <global_metadata>`, used by a PrintOutlet created in the :ref:`Basic Outlet <basic-outlet>` example.

    #. Create the :code:`ConditionalPrintOutlet` implementing :any:`Outlet` class. This outlet will accept one metadata key:

        * :code:`ConditionalPrintOutlet.SHOULD_PRINT` - whether record should be printed.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :start-at: class ConditionalPrintOutlet
        :end-at: """Whether

    #. Implement :code:`push` method, looping over all records and printing them if :code:`ConditionalPrintOutlet.SHOULD_PRINT` is set:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :start-at: def push
        :end-at: print(update

    #. Instantiate two inlets, one that always prints, other that never prints:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :start-at: random_int_inlet_on =
        :end-at: random_int_inlet_off =

    #. Instantiate :code:`ConditionalPrintOutlet` and add all nodes to a link

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :start-at: print_outlet =
        :end-at: name='should_print_metadata'

    #. Add to a planner and schedule.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python
        :start-at: planner =
        :end-at: planner.start

    Output:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> should_print_metadata.0 Record(payload=44, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
        >>> should_print_metadata.1 Record(payload=14, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
        >>> should_print_metadata.2 Record(payload=54, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
        >>> ...

    On each transfer :code:`ConditionalPrintOutlet` prints records incoming only from the :code:`random_int_inlet_on` that was constructed with global metadata that allows printing.

    Full example:

    .. literalinclude:: ../../examples/basic_metadata.py
        :language: python