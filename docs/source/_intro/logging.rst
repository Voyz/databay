.. _logging:

Logging
-------

All classes in Databay are configured to utilise a :any:`Python Logger <python:logging.Logger>` called :code:`databay` or its child loggers. Databay utilises a custom :any:`StreamHandler <python:logging.StreamHandler>` with the following signature:


.. code-block:: python

   %Y-%m-%d %H:%M:%S.milis|levelname| message (logger name)

.. rst-class:: mb-s

    For example:

.. code-block:: python

   2020-07-30 19:51:41.318|D| http_to_mongo.0 transfer (databay.Link)

.. rst-class:: mb-s
By default Databay will only log messages with :code:`WARNING` priority or higher. You can manually enable more verbose logging by calling:

.. code-block:: python

    logging.getLogger('databay').setLevel(logging.DEBUG)

    # Or do it only for a particular child logger:

    logging.getLogger('databay.APSPlanner').setLevel(logging.DEBUG)

You can attach new handlers to any of these loggers in order to implement custom logging behaviour - such as a :any:`FileHandler <logging.FileHandler>` to log into a file, or a separate :any:`StreamHandler <logging.StreamHandler>` to customise the print signature.