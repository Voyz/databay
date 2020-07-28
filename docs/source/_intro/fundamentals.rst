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

