import importlib

if importlib.util.find_spec('pymongo') is not None:
    from databay.outlets.mongo_outlet import MongoOutlet

from databay.outlets.print_outlet import PrintOutlet
from databay.outlets.csv_outlet import CsvOutlet
