import csv
import os
from pathlib import Path
from typing import List

from databay import Outlet, Update, Record, Link
from databay.inlets import RandomIntInlet
from databay.outlet import MetadataKey
from databay.outlets import CsvOutlet

class BatchOutlet(Outlet):

    BATCH_SPLIT: MetadataKey = 'BatchOutlet.BATCH_SPLIT'

    def __init__(self):
        super().__init__()

    def push(self, update: Update, batch:List[Record]):
        self.push_batch(update, batch)

    def push_batch(self, update:Update, batch:List[Record]):
        raise NotImplementedError()




class CsvBatchOutlet(BatchOutlet):

    def __init__(self, default_filepath, grouping_metadata_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_filepath = default_filepath
        self.grouping_metadata_key = grouping_metadata_key

    def push_batch(self, update:Update, batch:List[Record]):
            filepath = batch['filepath']
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, newline="") as f:

                writer = csv.DictWriter(f, batch[0].payload.keys())

                writer.writeheader()

                writer.write(batch)




class Store():
    def __init__(self, count_threshold : int = None, time_threshold: int = None, callbacks_list: List[callable] = None):
        self.count_threshold = count_threshold
        self.time_threshold = time_threshold
        self.callbacks_list = callbacks_list
        if self.callbacks_list is None:
            self.callbacks_list = []

        self.executables = []
        self.records = []
        
        if count_threshold is not None:
            self.executables.append(self.count_execute)
        if time_threshold is not None:
            self.executables.append(self.time_execute)

        self.executables = self.executables + self.callbacks_list

    # def iteration(self, records:List[Record]):
    #     rv = self.executable(records)
    #     if rv:
    #         return records
    #     else:
    #         return []

    def count_execute(self, records):
        if len(records) > self.count_threshold:
            return True
        else:
            return False

    def time_execute(self, records):
        ###
        self.time_threshold

    def execute(self, records):
        self.records += records

        for e in self.executables:
            if e(self.records):
                rv = self.records
                self.records = []
                return rv
            else:
                return []


def prime_execute(records):
    for record in records:
        if is_prime(record.payload):
            return True

    return False

size_threshold = get_size_threshold()

def size_execute(records):
    return get_size(records) > size_threshold



aapl_store = Store(count_threshold=1000, time_threshold=1000*60*3, callbacks_list=[prime_execute, size_execute])
tsla_store = Store(count_threshold=1000, time_threshold=1000*60*3, callbacks_list=[prime_execute, size_execute])
stores={'aapl': aapl_store, 'tsla': tsla_store}


def pull():
    records = some_pull()
    for record in records:
        record['metadata'][BatchOutlet.BATCH_SPLIT] = 'aapl'
# store = [CountStore(count=1000), TimeStore(time=1000*60*3), PrimeStore, SizeStore(size=100000)]
# stores.append(CountStore(count=100))
# stores.append(TimeStore(time=1000 * 60 * 3)) # 3 min
# outlet = CsvBatchOutlet(stores={'aapl': aapl_store, 'tsla': tsla_store}, grouping_metadata_key='filepath')
outlet = CsvBatchOutlet()


def group_by_collection(records: List[Record], key, type='metadata'):
    """
    Group the provided records by the collection name specified in each record's metadata. Global collection provided on construction is used if no collection is specified.

    :type records: list[:any:`Record`]
    :param records: Records to be grouped
    :return: Grouped records
    :rtype: Dict[str, :any:`Record`]
    """
    collections = {'default': []}

    for record in records:
        if type == 'metadata':
            collection_name = record.metadata.get(key, 'default')
        elif type == 'payload':
            collection_name = record.payload.get(key, 'default')

        if collection_name not in collections:
            collections[collection_name] = []

        if isinstance(record.payload, list):
            collections[collection_name] += record.payload
        else:
            collections[collection_name].append(record.payload)

    return collections

def filepath_split(batches):
    _batches = []
    for batch in batches:
        rv = group_by_collection(batch, 'filepath')
        _batches.append(rv)
    return _batches

def count_store_grouper(batches):
    _batches = []
    for batch in batches:
        r_by_symbol = group_by_collection(batch, 'symbol')
        for collection in r_by_symbol:
            store = stores[collection['symbol']]
            rv = store.execute(collection)
            if rv:
                _batches.append(rv)

    return _batches


groupers = []
groupers.append(count_store_grouper)
groupers.append(filepath_split)

link = Link(inlet, outlet, interval=1, groupers=groupers)