Records
-------

:any:`Records <Record>` are data objects that provide a unified interface for data handling across Databay. In addition to storing data produced by inlets, records may also carry individual metadata. This way information can be passed between inlets and outlets, facilitating a broad spectrum of custom implementations. For instance one CsvOutlet could be used for writing into two different csv files depending on which inlet the data came from.

.. image:: _static/images/databay_metadata_csv.png