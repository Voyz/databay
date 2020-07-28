Basic metadata
------------

.. literalinclude:: ../../examples/basic_metadata.py
    :language: python

.. code-block:: python

    >>> should_print_metadata.0 Record(payload=44, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
    >>> should_print_metadata.1 Record(payload=14, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
    >>> should_print_metadata.2 Record(payload=54, metadata={'PrintOutlet.SHOULD_PRINT': True, '__inlet__': "RandomIntInlet(metadata:{'PrintOutlet.SHOULD_PRINT': True})"})
    >>> ...