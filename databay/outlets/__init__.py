import importlib.util

if importlib.util.find_spec('pymongo') is not None:
    from databay.outlets.mongo_outlet import MongoOutlet
else:  # pragma: no cover
    def MongoOutlet(*args, **kwargs):
        raise ImportError(
            'PyMongo dependency is required for MongoOutlet. Fix by running: pip install "databay[MongoOutlet]"')

from databay.outlets.print_outlet import PrintOutlet
from databay.outlets.csv_outlet import CsvOutlet
from databay.outlets.null_outlet import NullOutlet
