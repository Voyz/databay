Inlets, Outlets and Links
-------------------------

Databay treats data transfer as a unidirectional graph, where data flows from :any:`Inlet` nodes to :any:`Outlet` nodes. An example of an inlet and outlet could be an HTTP request client and a CSV writer respectively.

.. image:: _static/images/databay_data_flow.png

The relationship between the inlets and outlets is explicitly defined as a :any:`Link`.

.. image:: _static/images/databay_basic_graph.png

One link may connect multiple inlets and outlets.

.. image:: _static/images/databay_many_nodes.png

One inlet or outlet can be connected through multiple links.

.. image:: _static/images/databay_many_links.png

Each link contains an interval at which it will run the data transfer. This interval is specified on construction with the :code:`interval` parameter of type :any:`datetime.timedelta`.

.. code-block:: python

    Link([inlets], [outlets], interval=timedelta(minutes=10))


During transfer, a link will pull data from all its inlets and then push that collected data to all its outlets. One quantity of data is represented with a :any:`Record`.

.. image:: _static/images/databay_transfer_basic.png

Both pulling and pushing is executed asynchronously, yet pushing only starts once all inlets have finished returning their data.