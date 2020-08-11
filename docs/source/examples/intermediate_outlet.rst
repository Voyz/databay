Intermediate Outlet
-------------------

.. _python_io: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files

.. container:: tutorial-block

    This example demonstrates an outlet that writes the incoming records into a file. It showcases what a realistic implementation of :any:`Outlet` may look like.

    #. Create the :code:`FileOutlet` implementing :any:`Outlet` class. This outlet will accept two metadata keys:

        * :code:`FileOutlet.FILEPATH` - specifying the file that the record should be written into.
        * :code:`FileOutlet.FILE_MODE` - specifying the write mode using `Python's default IO <python_io_>`_.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/intermediate_outlet.py
        :language: python
        :start-at: class FileOutlet
        :end-at: """Write


    #. We give an option to specify :code:`default_filepath` and :code:`default_file_mode` when constructing this outlet.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/intermediate_outlet.py
        :language: python
        :start-at: def __init__(
        :end-at: self.default_file_mode =

    #. Implement :code:`push` method, looping over all records and reading their metadata.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/intermediate_outlet.py
        :language: python
        :start-at: def push(
        :end-at: file_mode =

    #. Write the record according to the :code:`filepath` and :code:`file_mode` found.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/intermediate_outlet.py
        :language: python
        :start-at: with open(
        :end-at: f.write(

    #. Instantiate :code:`FileOutlet` and :any:`RandomIntInlet` provided with a metadata dictionary.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/intermediate_outlet.py
        :language: python
        :start-at: metadata =
        :end-at: file_outlet = FileOutlet

    #. Create a link, add to a planner and schedule.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/intermediate_outlet.py
        :language: python
        :start-at: link = Link
        :end-at: planner.start

    Creates :code:`outputs/random_ints.txt` file:

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

    Full example:

    .. literalinclude:: ../../examples/intermediate_outlet.py
        :language: python