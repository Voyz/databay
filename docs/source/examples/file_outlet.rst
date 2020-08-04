File Outlet
------------

.. _python_io: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files

.. container:: tutorial-block

    This example demonstrates an outlet writes the incoming records into a file. It showcases what a realistic implementation of :any:`Outlet` may look like.

    #. Create the :code:`FileOutlet` implementing :any:`Outlet` class. This outlet will accept two metadata keys:

        * :code:`FileOutlet.FILEPATH` - specifying the file that the record should be written into.
        * :code:`FileOutlet.FILE_MODE` - specifying the write mode using `Python's default IO <python_io_>`_.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/file_outlet.py
        :language: python
        :lines: 9-12


    #. We expect :code:`default_filepath` and :code:`default_file_mode` to be provided when constructing this outlet.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/file_outlet.py
        :language: python
        :lines: 14-21

    #. Implement :code:`push` method, looping over all record and reading their metadata.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/file_outlet.py
        :language: python
        :lines: 23-26

    #. Write the record according to the :code:`filepath` and :code:`file_mode` found.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/file_outlet.py
        :language: python
        :lines: 28-29

    #. Instantiate :code:`FileOutlet` and :any:`RandomIntInlet` provided with a metadata dictionary.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/file_outlet.py
        :language: python
        :lines: 32-37


    Full example:

    .. literalinclude:: ../../examples/file_outlet.py
        :language: python

    Produces :code:`outputs/random_ints.txt` file:

    .. rst-class:: highlight-small
    .. code-block:: none
        
        1
        76
        52
        76
        64
        89
        71
        12
        70
        74
        ...