.. _batchers:

Batchers
=========

.. contents::
    :local:
    :backlinks: entry


By default outlets will be given all produced records at the same time. Batchers are a middleware which allows you to break that list of records into batches. Each batch is then fed into outlets separately, allowing outlets to process an entire batch individually at the same time, instead of processing each record one by one.



Simple example
--------------

Following batcher will divide the records into batches based on their payload 'name' attribute.

.. code-block:: python

    def batcher_by_name(batches: List[List[Record]]):
        result = []
        for batch in batches:
            new_batch = {}
            for record in batch:
                new_batch[record.payload['name']] = record

            result.append(list(new_batch.values()))

    link = Link(..., batchers=batcher_by_name)

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


Batchers explained
-------------------

.. rst-class:: mb-s

    A **batcher** is a :any:`callable` function that accepts a list of batches and returns a list of batches with a different shape.

    A **list of batches** is a two-dimensional list containing :any:`Records <Record>` divided into sub-lists.

Each of these sub-lists is called a **batch**.


Fox example:

.. container:: tutorial-block

    #. Consider an inlet that produces six records with a simple payload. This first list is a **list of records**, as all records are contained within it.

        .. rst-class:: highlight-small
        .. code-block:: python

            [0,1,2,3,4,5]

    #. When divided by a pairing batcher, that list may be turned into the following two-dimensional list. This second list is a **list of batches**, as it contains the records divided into three sub-lists.

        .. rst-class:: highlight-small
        .. code-block:: python

            [[0,1], [2,3], [3,4]]




    #. Each element of the list of batches is a **batch**, as it represents one sub-list containing the records.


        .. rst-class:: highlight-small
        .. code-block:: python

            [0,1]

Note that:

 * All records contained in all batches should equal to the list of records.
 * First batcher is always provided with one batch containing all records. This is due to the fact that batchers are order-agnostic, allowing you to swap them around expecting consistent behaviour.

After batching
---------------

Once records are divided into batches, each batch is fed into the outlets as if it was an individual list of records. Depending on the particular implementation, outlets may expect that and process the entire batch at the same time. If a particular outlet doesn't support batch processing, the result of batching will effectively be nullified except for the order in which the records will be consumed.

The following examples illustrate how the records are fed into the outlets with and without batchers.

Without batchers:

.. code-block:: python

    print(records)
    # [0,1,2,3,4,5]

    for outlet in self.outlets:
        outlet.push(records)

In this case :code:`outlet.push` is called once with the entire list of records :code:`[0,1,2,3,4,5]`.

With batchers:

.. code-block:: python

    print(records)
    # [0,1,2,3,4,5]

    batches = [records] # the default batch contains all records
    for batcher in batchers:
        batches = batcher(batches) # the batchers turn the list of records into batches

    print(batches)
    # [[0,1],[2,3],[4,5]]

    for batch in batches:
        for outlet in self.outlets:
            outlet.push(batch)

In this case :code:`outlet.push` is called three times, each time receiving a different batch: :code:`[0,1]`, :code:`[2,3]` and :code:`[4,5]`.

Observe that when no batchers are provided, there is only one batch containing all records. This will provide all outlets with all records at the same time, effectively nullifying the batches' functionality described in this section.

Best practices
--------------

.. rubric:: Responsibility

Databay doesn't make any assumptions about batchers - you can implement any type of batchers that may suit your needs. This also means Databay will not ensure the records aren't corrupted by the batchers. Therefore you need to be conscious of what each batcher do to the data.

.. rubric:: Only batching

Note that you should only use batchers' functionality to subdivide the records into batches. Do not transform or filter the records using batchers - you can use :any:`Processors <processors>` for that instead. If a list of batches was to be flattened it should return the list of records as originally produced by the inlets, except for the order of records.

.. code-block:: python

    print(records)
    # [0,1,2,3,4,5]

    batches = [records] # the default batch contains all records
    for batcher in batchers:
        batches = batcher(batches)

    flat_batches = [record for batch in batches for record in batch] # flatten the batches

    # do both list contain same elements regardless of the order?
    print(set(records) == set(flat_batches))
    # True

.. rubric:: Adhere to correct structure

Databay expects to work with either one- or two-dimensional data, depending on whether batchers are used. One-dimensional being a list of records (ie. without batching), two-dimensional being a list of batches (ie. with batching). In either case, outlets will be provided with a list (or sub-list) of records and are expected to process these as a one-dimensional list.

Introducing further sub-list breakdowns - eg. batches containing batches - is not expected and such subsequent subdivisions will not be indefinitely iterated. If you choose to introduce further subdivisions ensure the outlets you use are familiar with such data structure and are able to process it accordingly.


