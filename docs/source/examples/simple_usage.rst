Simple usage
------------

.. container:: tutorial-block

    This is a simple example of how data can be produced, transferred and consumed in Databay. It uses built-in :any:`HttpInlet` for producing data using a test URL and :any:`MongoOutlet` consuming it using MongoDB.

    #. Create an inlet for data production:

    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :lines: 9

    #. Create an outlet for data consumption:

    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :lines: 10

    #. Add the two to a link that will handle data transfer between them:

    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :lines: 11-12

    #. Create a planner, add the link and start scheduling:

    .. literalinclude:: ../../examples/simple_usage.py
        :language: python
        :lines: 15-17

    Full code:

    .. literalinclude:: ../../examples/simple_usage.py
        :language: python

    Produces:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> 2020-07-30 19:51:36.313|I| Added link: Link(name:http_to_mongo, inlets:[HttpInlet(metadata:{})], outlets:[MongoOutlet()], interval:0:00:05) (databay.BasePlanner)
        >>> 2020-07-30 19:51:36.314|I| Starting APSPlanner(threads:30) (databay.BasePlanner)
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