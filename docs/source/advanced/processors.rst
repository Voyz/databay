.. _processors:

Processors
==========

.. contents::
    :local:
    :backlinks: entry

Processors are a middleware pipeline that alters the records transferred from inlets to outlets. Two most common usages of these would be:

* Filtering - removing some or all records before feeding them to outlets.
* Transforming - altering the records before feeding them to outlets.

Simple example
--------------

.. code-block:: python

    # Example filtering
    def only_large_numbers(records: List[Records]):
        result = []
        for record in records:
            if record.payload >= 100:
                result.push(record)
        return result

    # Example transforming:
    def round_to_integers(records: List[Records]):
        for record in records:
            record.payload = round(record.payload)
        return records

    # pass to a link
    link = Link(..., processors=[only_large_numbers, round_to_integers])

.. rst-class:: mb-s

    The processor pipeline used in the above example will turn the following list:

    .. rst-class:: highlight-small
    .. code-block:: python

        [99.999, 200, 333.333]

.. rst-class:: mb-s

    into:

    .. rst-class:: highlight-small
    .. code-block:: python

        [200, 333]

Note that :code:`99.999` got filtered out given the order of processors. If we were to swap the processors, the rounding would occur before filtering, allowing all three results through the filter.

Processors explained
--------------------

A processor is a :any:`callable` function that accepts a list of records and returns a (potentially altered) list of records.

Processors are called in the order in which they are passed, after all inlets finish producing their data. The result of each processor is given to the next one, until finally the resulting records continue the transfer normally.

.. _link-outlet-processors:

Link vs Outlet processors
--------------------------

Databay supports two types of processors, depending on the scope at which they operate. This distinction can be used to determine at which level a particular processor is to be applied.

* :any:`Link processor <Link>` - passed to links and applied to all records transferred by that link.
* :any:`Outlet processor <Outlet>` - passed to outlets and applied only to records passed to the particular outlet.

For example:

* :any:`Link processor <Link>` - A filtering processor that removes duplicate records produced by an inlet could be applied to all records at link level.

.. code-block:: python

    def remove_duplicates(records: List[Record]):
        result = []
        for record in records:
            if record not in result:
                result.append(record)
        return result

    link = Link(..., processors=remove_duplicates)

* :any:`Outlet processor <Outlet>` - A filtering processor that filters out records already existing in a CSV file could be applied only to the CsvOutlet, preventing duplicate records from being written to a CSV file, yet otherwise allowing all records to be consumed by the other outlets in the link.

.. code-block:: python

    def filter_existing(records: List[Record]):
        with open(os.fspath('./data/records.csv'), 'r') as f:
            reader = csv.DictReader(csv_file)
            existing = []
            for row in reader:
                for key, value in row.items():
                    existing.append(value)

        result = []
        for record in records:
            if record.payload not in existing:
                result.append(record)
        return result

    csv_outlet = CsvOutlet(..., processors=filter_existing)
    link = Link(inlets, csv_outlet, ...)

Link processors are used before :any:`Splitters <splitters>`, while Outlet processors are used after.


Best practices
--------------

.. rubric:: Responsibility

Databay doesn't make any further assumptions about processors - you can implement any type of processors that may suit your needs. This also means Databay will not ensure the records aren't corrupted by the processors, therefore you need to be conscious of what each processor do to the data.

If you wish to verify the integrity of your records after processing, attach an additional processor at the end of your processor pipeline that will validate the correctness of your processed records before sending it off to the outlets.
