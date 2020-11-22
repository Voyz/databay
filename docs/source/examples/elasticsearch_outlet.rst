ElasticSearch Outlet
--------------------

.. container:: tutorial-block

    In this example we create an implementation of :any:`Outlet` that indexes documents to a running Elasticsearch instance. 
    
    **Note**: this example assumes that Elasticsearch is correctly configured and that the index you are indexing documents to exists
    with the appropriate mappings.  

    #. Extend the :any:`Outlet` with new parameters required when constructing: :code:`es_client` an instance of the elasticsearch python client and :code:`index_name` the name of a pre-existing index in the running cluster.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: class ElasticSearchIndexerOutlet
        :end-at: raise RuntimeError(f"Index '{self.index_name}' does not exist ")

    #. In this implementation of the :code:`push` method there are a few custom behaviors specified. As we iterate over every incoming record:

        * We use the dict keys from the current record's :code:`payload` as our unique document id.
        * The flag :code:`self.overwrite_documents` determines whether we will check if an id already exists. 
        * If :code:`self.overwrite_documents` is True we simply index the document and :code:`_id` without doing any check. 
        * Otherwise we use the client to check if :code:`_id` exists in the index. If it does we skip and log that it already exists. Otherwise it is indexed as normal. 

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: def push
        :end-before: class DummyTextInlet

    #. This simple :any:`Inlet` takes a list of strings as its main parameter. In it's :code:`pull` method it randomly selects one and returns the string and an incrementing id as a :code:`dict`. We'll use this to pass documents to our Elasticsearch Outlet. 

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: class DummyTextInlet
        :end-at:   return {self._id: text_selection}

    #. Instantiate our simple :any:`Inlet` as well as an instance of :code:`ElasticSearchIndexerOutlet` with the default parameter for :code:`overwrite_documents`.

        * We use the official elasticsearch python client for `es_client`. 
        * This example assumes `my-test-index` exists already in our elasticsearch cluster. 
        * The link is setup to index a new document every 2 seconds. 
    
    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python
        :start-at: es_client = elasticsearch.Elasticsearch(timeout=30)
        :end-at:  planner.start

    Output:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> 2020-11-22 18:26:23.597|I| Indexed document with id 1 (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:26:25.498|I| Indexed document with id 2 (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:26:27.503|I| Indexed document with id 3 (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:26:29.497|I| Indexed document with id 4 (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:26:31.495|I| Indexed document with id 5 (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:26:33.492|I| Indexed document with id 6 (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:26:35.492|I| Indexed document with id 7 (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:26:37.493|I| Indexed document with id 8 (databay.elasticsearch_outlet)
    
    Output (if :code:`overwrite_documents` is set to :code:`False`):

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> 2020-11-22 18:32:08.052|I| Document already exists for id 1. Skipping. (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:32:10.050|I| Document already exists for id 2. Skipping. (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:32:12.047|I| Document already exists for id 3. Skipping. (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:32:14.049|I| Document already exists for id 4. Skipping. (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:32:16.046|I| Document already exists for id 5. Skipping. (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:32:18.047|I| Document already exists for id 6. Skipping. (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:32:20.047|I| Document already exists for id 7. Skipping. (databay.elasticsearch_outlet)
        >>> 2020-11-22 18:32:22.047|I| Document already exists for id 8. Skipping. (databay.elasticsearch_outlet)



    Full example:

    .. literalinclude:: ../../examples/elasticsearch_outlet.py
        :language: python