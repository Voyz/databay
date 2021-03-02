.. _splitters:

Splitters
=========

Splitters are a middleware that splits the records into batches. Each batch is then fed into outlets separately, allowing for outlets to process an entire batch at the same time, instead of processing each record one by one.

For example:

.. code-block:: python

    def splitter_by_name(batches: List[List[Record]]):
        result = []
        for batch in batches:
            split = {}
            for record in batch:
                split[record.payload.name] = record

            result += list(split.values())

    link = Link(..., splitters=splitter_by_name)

A splitter is a :any:`callable` function that accepts a list batches and returns a list of batches.

Batches
-------

A *batch* is a sub-list of records.

A *list of batches* is a list containing the records divided into sub-lists.

* Consider an inlet that produces six records with the following payload:

    :code:`[0,1,2,3,4,5]`

* When split by a pairing splitter, that list may be turned into the following:

    :code:`[[0,1], [2,3], [3,4]]`

* The first batch in this list is the following:

    :code:`[0,1]`

The first list is a *list of records*, as all records are contained in that list.

The second list is a *list of batches*, as it contains the records split into three sub-lists.

Each element of the list of batches is a *batch*, as it represents one sub-list containing the records. All records contained in all batches should equal to the list of records.

After splitting
---------------

Once records are split into batches, each batch is fed into the outlets as if it was an individual list of records. Depending on the particular implementation, outlets may expect that and process the entire batch at the same time. If a particular outlet doesn't support batch processing, the result of splitting will effectively be nullified except for the order in which the records will be consumed.

The following examples illustrate how the records are fed into the outlets with and without splitters.

Without splitters:

.. code-block:: python

    print(records)
    # [0,1,2,3,4,5]

    for outlet in self.outlets:
        outlet.push(records)

In this case :code:`outlet.push` is called once with the entire list of records :code:`[0,1,2,3,4,5]`.

With splitters:

.. code-block:: python

    print(records)
    # [0,1,2,3,4,5]

    batches = [records] # the default batch contains all records
    for splitter in splitters:
        batches = splitter(batches) # the splitters turn the list of records into batches

    print(batches)
    # [[0,1],[2,3],[4,5]]

    for batch in batches:
        for outlet in self.outlets:
            outlet.push(batch)

In this case :code:`outlet.push` is called three times, each time receiving a different batch: :code:`[0,1]`, :code:`[2,3]` and :code:`[4,5]`.

Observe that when no splitters are provided, there is only one batch containing all records. This will provide all outlets with all records at the same time, effectively nullifying the batches' functionality described in this section.

Best practices
--------------

.. rubric:: Responsibility

Databay doesn't make any assumptions about splitters - you can implement any type of splitters that may suit your needs. This also means Databay will not ensure the records aren't corrupted by the splitters. Therefore you need to be conscious of what each splitter do to the data.

.. rubric:: Only split

Note that you should only use splitters' functionality to subdivide the records into batches. Do not transform or filter the records using splitters - you can use :any:`Processors <processors>` for that instead. If a list of batches was to be flattened it should return the list of records as originally produced by the inlets, except for the order of records.

.. code-block:: python

    print(records)
    # [0,1,2,3,4,5]

    batches = [records] # the default batch contains all records
    for splitter in splitters:
        batches = splitter(batches)

    flat_batches = [record for batch in batches for record in batch] # flatten the batches

    # do both list contain same elements regardless of the order?
    print(set(records) == set(flat_batches))
    # True