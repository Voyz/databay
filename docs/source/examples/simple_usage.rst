Simple usage
------------

.. container:: tutorial-block

    This is a simple example of how data can be produced, transferred and consumed in Databay. It uses built-in :any:`HttpInlet` for producing data using a test URL and :any:`MongoOutlet` consuming it using MongoDB.

    #. Create an inlet for data production:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :start-at: http_inlet = HttpInlet
        :end-at: http_inlet = HttpInlet

    #. Create an outlet for data consumption:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :start-at: mongo_outlet = MongoOutlet
        :end-at: mongo_outlet = MongoOutlet

    #. Add the two to a link that will handle data transfer between them:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :start-at: link = Link
        :end-at: tags='http_to_mongo'

    #. Create a planner, add the link and start scheduling:

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :start-at: planner =
        :end-at: planner.start

    #. (Optional) In this example the databay logger is configured to display all messages. See :ref:`Logging <logging>` for more information.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :start-at: .getLogger('databay')
        :end-at: .getLogger('databay')


    Output:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> 2020-07-30 19:51:36.313|I| Added link: Link(tags:['http_to_mongo'], inlets:[HttpInlet(metadata:{})], outlets:[MongoOutlet()], interval:0:00:05) (databay.BasePlanner)
        >>> 2020-07-30 19:51:36.314|I| Starting ApsPlanner(threads:30) (databay.BasePlanner)

        >>> 2020-07-30 19:51:41.318|D| http_to_mongo.0 transfer (databay.Link)
        >>> 2020-07-30 19:51:41.318|I| http_to_mongo.0 pulling https://jsonplaceholder.typicode.com/todos/1 (databay.HttpInlet)
        >>> 2020-07-30 19:51:42.182|I| http_to_mongo.0 received https://jsonplaceholder.typicode.com/todos/1 (databay.HttpInlet)
        >>> 2020-07-30 19:51:42.188|I| http_to_mongo.0 insert [{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False}] (databay.MongoOutlet)
        >>> 2020-07-30 19:51:42.191|I| http_to_mongo.0 written [{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False, '_id': ObjectId('5f22c25ea7aca516ec3fcf38')}] (databay.MongoOutlet)
        >>> 2020-07-30 19:51:42.191|D| http_to_mongo.0 done (databay.Link)

        >>> 2020-07-30 19:51:46.318|D| http_to_mongo.1 transfer (databay.Link)
        >>> 2020-07-30 19:51:46.318|I| http_to_mongo.1 pulling https://jsonplaceholder.typicode.com/todos/1 (databay.HttpInlet)
        >>> 2020-07-30 19:51:46.358|I| http_to_mongo.1 received https://jsonplaceholder.typicode.com/todos/1 (databay.HttpInlet)
        >>> 2020-07-30 19:51:46.360|I| http_to_mongo.1 insert [{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False}] (databay.MongoOutlet)
        >>> 2020-07-30 19:51:46.361|I| http_to_mongo.1 written [{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False, '_id': ObjectId('5f22c262a7aca516ec3fcf39')}] (databay.MongoOutlet)
        >>> 2020-07-30 19:51:46.362|D| http_to_mongo.1 done (databay.Link)
        ...



    Above log can be read as follows:

    * At first the planner adds the link provided and starts scheduling:

        .. rst-class:: highlight-small
        .. code-block:: python

            Added link: Link(tags:['http_to_mongo'], inlets:[HttpInlet(metadata:{})], outlets:[MongoOutlet()], interval:0:00:05)
            Starting ApsPlanner(threads:30)

    * Once scheduling starts, link will log the beginning and end of each transfer:

        .. rst-class:: highlight-small
        .. code-block:: python

            http_to_mongo.0 transfer

        Note the :code:`http_to_mongo.0` prefix in the message. It is the string representation of the :any:`Update` object that represents each individual transfer executed by that particular link. :code:`http_to_mongo` is the tag of the link, while :code:`0` represents the incremental index of the transfer.

    * Then :any:`HttpInlet` logs its data production:

        .. rst-class:: highlight-small
        .. code-block:: python

                http_to_mongo.0 pulling https://jsonplaceholder.typicode.com/todos/1
                http_to_mongo.0 received https://jsonplaceholder.typicode.com/todos/1

    * Followed by :any:`MongoOutlet` logging its data consumption:

        .. rst-class:: highlight-small
        .. code-block:: python

            http_to_mongo.0 insert [{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False}]
            http_to_mongo.0 written [{'userId': 1, 'id': 1, 'title': 'delectus aut


    * Finally, link reports completing its first transfer:

        .. rst-class:: highlight-small
        .. code-block:: python

            http_to_mongo.0 done



    Full example:

    .. literalinclude:: ../../examples/simple_usage.py
        :language: python

