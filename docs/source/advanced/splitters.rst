.. _splitters:

Splitters
=========

.. contents::
    :local:
    :backlinks: entry


By default outlets will be given all produced records at the same time. Splitters are a middleware which allows you to break that list of records into batches. Each batch is then fed into outlets separately, allowing outlets to process an entire batch individually at the same time, instead of processing each record one by one.



Simple example
--------------

Following splitter will split the records into batches based on their payload 'name' attribute.

.. code-block:: python

    def splitter_by_name(batches: List[List[Record]]):
        result = []
        for batch in batches:
            split = {}
            for record in batch:
                split[record.payload['name']] = record

            result.append(list(split.values()))

    link = Link(..., splitters=splitter_by_name)

.. rst-class:: mb-s

    Which will turn the following list of records:

.. rst-class:: highlight-small
.. code-block:: python

    [
        {'name': 'a', 'value': 1},
        {'name': 'a', 'value': 2},
        {'name': 'b', 'value': 3},
        {'name': 'b', 'value': 4}
    ]

.. rst-class:: mb-s

    into the following list of batches:

.. rst-class:: highlight-small
.. code-block:: python

    [
        [
            {'name': 'a', 'value': 1},
            {'name': 'a', 'value': 2}
        ],
        [
            {'name': 'b', 'value': 3},
            {'name': 'b', 'value': 4}
        ]
    ]


Splitters explained
-------------------

A splitter is a :any:`callable` function that accepts a list of batches and returns a list of batches.

A *list of batches* is a two-dimensional list containing the records divided into sub-lists.

Each of these sub-lists is called a *batch*.

* Consider an inlet that produces six records with the following payload:

    :code:`[0,1,2,3,4,5]`

* When split by a pairing splitter, that list may be turned into the following:

    :code:`[[0,1], [2,3], [3,4]]`

* The first batch in this list is the following:

    :code:`[0,1]`

The first list is a *list of records*, as all records are contained in that list.

The second list is a *list of batches*, as it contains the records split into three sub-lists.

Each element of the list of batches is a *batch*, as it represents one sub-list containing the records. All records contained in all batches should equal to the list of records.

Note that first splitter is always provided with one batch containing all records. This is due to the fact that splitters are order-agnostic, allowing you to swap them around expecting consistent behaviour.

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

.. rubric:: Adhere to correct structure

Databay expects to work with either one- or two-dimensional data, depending on whether splitters are used. One-dimensional being a list of records (ie. without splitting), two-dimensional being a list of batches (ie. with splitting). In either case, outlets will be provided with a list (or sub-list) of records and are expected to process these as a one-dimensional list.

Introducing further sub-list breakdowns - eg. batches containing batches - is not expected and such subsequent subdivisions will not be indefinitely iterated. If you choose to introduce further subdivisions ensure the outlets you use are familiar with such data structure and are able to process it accordingly.


