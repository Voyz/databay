Elasticsearch Outlet
--------------------

.. container:: tutorial-block

    In this example we create an implementation of :any:`Outlet` that indexes records as documents to a running Elasticsearch instance. 
    
    **Note**: this example assumes that Elasticsearch is correctly configured and that the index you are indexing documents to exists
    with the appropriate mappings. For more details see the official Elasticsearch Python client_
     
    .. _client: https://elasticsearch-py.readthedocs.io


    #. Extend the :any:`Outlet` with new parameters required when constructing: :code:`es_client` - an instance of the elasticsearch python client and :code:`index_name` the name of a pre-existing index in the running cluster.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: class ElasticsearchIndexerOutlet
        :end-at: raise RuntimeError(f"Index '{self.index_name}' does not exist ")

    #. In this implementation of the :code:`push` method there are a few custom behaviors specified. As we iterate over every incoming record:

        * We use the dict keys from the current record's :code:`payload` as our unique document ID.
        * The flag :code:`self.overwrite_documents` determines whether we will check if an id already exists. 
        * If :code:`self.overwrite_documents` is True we simply index the document and :code:`_id` without doing any check. 
        * Otherwise we use the client to check if :code:`_id` exists in the index. If it does we skip and log that it already exists. Otherwise it is indexed as normal. 

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: def push
        :end-before: class DummyTextInlet

    #. This simple :any:`Inlet` takes a list of strings as its main parameter. In its :code:`pull` method it randomly selects one and returns the string and an incrementing id as a :code:`dict`. We'll use this to pass documents to our Elasticsearch Outlet. 

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: class DummyTextInlet
        :end-at:   return {self._id: text_selection}

    #. Instantiate our simple :any:`Inlet` as well as an instance of :code:`ElasticsearchIndexerOutlet` with the default parameter for :code:`overwrite_documents`.

        * We use the official Elasticsearch Python client for `es_client`. 
        * This example assumes :code:`my-test-index` exists already in our elasticsearch cluster. 
    
    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: es_client = elasticsearch.Elasticsearch(timeout=30)
        :end-at:  es_client, "my-test-index")
    
    #. Tie it all together using :any:`Link` AND :any:`Planner`

        * The link is setup to index a new document every 2 seconds. 

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: link = Link
        :end-at:  planner.start()

    Output:

        * From the logs we can see that the records are being written into our Elasticsearch index.

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> Indexed document with id 1 
        >>> Indexed document with id 2 
        >>> Indexed document with id 3 
        >>> Indexed document with id 4 
        >>> Indexed document with id 5 
        >>> Indexed document with id 6 
        >>> Indexed document with id 7 
        >>> Indexed document with id 8 
    
    Output (if :code:`overwrite_documents` is set to :code:`False`):

        * From the logs we can see that the record ID's so far have already been written into our Elasticsearch index.
        

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> Document already exists for id 1. Skipping. 
        >>> Document already exists for id 2. Skipping. 
        >>> Document already exists for id 3. Skipping. 
        >>> Document already exists for id 4. Skipping. 
        >>> Document already exists for id 5. Skipping. 
        >>> Document already exists for id 6. Skipping. 
        >>> Document already exists for id 7. Skipping. 
        >>> Document already exists for id 8. Skipping. 


    Full example:

    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python