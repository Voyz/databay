Motivation
----------

The data flow in Databay is different from a more widely adopted `Observer Pattern <ObserverPattern_>`_, where data production and propagation are represented by one object, and consumption by another. In Databay data production and propagation is split between the :any:`Inlet` and :any:`Link` objects. This results in a data flow model in which each stage - data transfer, production and consumption - is independent from the others. :any:`Inlets <Inlet>` are only concerned with producing data, :any:`Outlets <Outlet>` only with consuming data and :any:`Links <Link>` only with transferring data. Such a model is motivated by `separation of concerns <soc_>`_ and by facilitating custom implementation of data producers and consumers.
