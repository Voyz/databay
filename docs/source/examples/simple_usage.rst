Simple usage
------------


.. literalinclude:: ../../examples/simple_usage.py
    :language: python

.. code-block:: python

    >>> 2020-07-28 17:51:16.313|I| Added link: Link(name:http_to_mongo, inlets:[HttpInlet(metadata:{})], outlets:[MongoOutlet()], interval:0:00:05) (databay.BasePlanner)
    >>> 2020-07-28 17:51:16.313|I| Starting APSPlanner(threads:30) (databay.BasePlanner)
    >>> 2020-07-28 17:51:21.314|I| http_to_mongo.0 pulling https://jsonplaceholder.typicode.com/todos/1 (databay.HttpInlet)
    >>> 2020-07-28 17:51:21.583|I| http_to_mongo.0 received https://jsonplaceholder.typicode.com/todos/1 (databay.HttpInlet)
    >>> 2020-07-28 17:51:21.589|I| http_to_mongo.0 insert [{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False}] (databay.MongoOutlet)
    >>> 2020-07-28 17:51:21.591|I| http_to_mongo.0 written [{'userId': 1, 'id': 1, 'title': 'delectus aut autem', 'completed': False, '_id': ObjectId('5f200329e4a644428ac18ebc')}] (databay.MongoOutlet)
