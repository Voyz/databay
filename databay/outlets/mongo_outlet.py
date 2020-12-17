"""
.. warning::
    :any:`MongoOutlet` requires `PyMongo <https://pymongo.readthedocs.io/en/stable/>`_ to function. Please install required dependencies using:

    .. code-block:: python

        pip install "databay[MongoOutlet]"
"""


import functools
import logging
from typing import List

import pymongo

from databay.outlet import Outlet, MetadataKey
from databay import Record

_LOGGER = logging.getLogger('databay.MongoOutlet')


class MongoCollectionNotFound(Exception):
    """ Raised when requested collection does not exist in the database."""
    pass


def ensure_connection(fn):
    """
    Ensure the MongoDB connection is established before running the function.

    :type fn: :any:`Callable <typing.Callable>`
    :param fn: Function to decorate
    """
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        if self._db is None:
            self.connect()
            # raise RuntimeError('Database is not connected')
        return fn(self, *args, **kwargs)
    return wrapper


class MongoOutlet(Outlet):
    """
    Outlet for pushing data into a MongoDB instance. Pushes are executed synchronously.
    """

    MONGODB_COLLECTION: MetadataKey = 'MongoOutlet.MONGODB_COLLECTION'
    """ Name of collection to write to. """

    def __init__(self, database_name: str = 'databay', collection: str = 'default_collection', host: str = None, port: str = None):
        """

        :type database_name: str
        :param database_name: Name of the MongoDB database to write to.
            |default| :code:`'databay'`

        :type collection: str
        :param collection: Global name of the collection to write to. This can be overwritten by records' metadata.MONGODB_COLLECTION parameter.
            |default| :code:`'default_collection'`

        :type host: str
        :param host: Address of MongoDB host.
            |default| :code:`None` (PyMongo defaults to :code:`'localhost'`)

        :type port: int
        :param port: Port of the MongoDB host.
            |default| :code:`None` (PyMongo defaults to :code:`27017`)
        """
        super().__init__()

        self.host = host
        self.port = port
        self.database_name = database_name
        self.collection = collection
        self._client = None
        self._db = None  # _db == None means disconnected
        self._collections = []

    def _group_by_collection(self, records: List[Record]):
        """
        Group the provided records by the collection name specified in each record's metadata. Global collection provided on construction is used if no collection is specified.

        :type records: list[:any:`Record`]
        :param records: Records to be grouped
        :return: Grouped records
        :rtype: Dict[str, :any:`Record`]
        """
        collections = {}

        for record in records:
            collection_name = record.metadata.get(
                self.MONGODB_COLLECTION, self.collection)

            if collection_name not in collections:
                collections[collection_name] = []

            if isinstance(record.payload, list):
                collections[collection_name] += record.payload
            else:
                collections[collection_name].append(record.payload)

        return collections

    @ensure_connection
    def push(self, records: [Record], update):
        """
        |decorated| :any:`ensure_connection`

        Write records into the database. Writes are executed synchronously.

        :type records: list[:any:`Record`]
        :param records: List of records generated by inlets. Each top-level element of this array corresponds to one inlet that successfully returned data. Note that inlets could return arrays too, making this a nested array.

        :type update: :any:`Update`
        :param update: Update object representing the particular Link transfer.
        """

        # Make sure no writes happen before start and after shutdown.
        if not self.active:
            return False

        records_by_collections = self._group_by_collection(records)

        for collection_name, collection_records in records_by_collections.items():

            try:
                collection = self._get_collection(collection_name)
            except MongoCollectionNotFound:
                self._add_collection(collection_name)
                collection = self._get_collection(collection_name)

            _LOGGER.info(f'{update} insert {collection_records}')
            collection.insert_many(collection_records)
            _LOGGER.info(f'{update} written {collection_records}')

        return True

    def connect(self, database_name: str = None) -> bool:
        """
        Connect to the specified database. Returns True if already connected to the specified database. Disconnects from any existing databases if the specified database is different.

        :type database_name: str
        :param database_name: Name of the database to connect to. |default| :code:`None` (Connects to default database name if not specified`)

        :return: Returns True if already connected to the database specified.
        :rtype: bool
        """

        if database_name is None:
            database_name = self.database_name

        if self._client is not None and self._db is not None:
            if self._db.name == database_name:
                return True
            else:
                self.disconnect()

        self._client = pymongo.MongoClient(host=self.host, port=self.port)
        self._db = self._client[database_name]
        return False

    def disconnect(self):
        """
        Disconnect from the database if currently connected.
        """
        if self._client is not None:
            self._client.close()
            self._client = None

        if self._db is not None:
            self._db = None

    def on_start(self):
        """
        Connect to the MongoDB host on start.
        """
        self.connect()

    def on_shutdown(self):
        """
        Disconnect from the MongoDB host on shutdown.
        """
        self.disconnect()

    def _get_collection(self, collection: str):
        """
        Get a collection from the database.

        :type collection: str
        :param collection: Collection to acquire from the database.

        :rises: :any:`MongoCollectionNotFound` if collection is not found in the database.

        :return: Retrieved collection
        :rtype: PyMongo Collection
        """
        if str(collection) not in self._collections:
            self._collections = self._db.list_collection_names()
            if str(collection) not in self._collections:
                raise MongoCollectionNotFound(
                    'Collection called "%s" not found. Please create the collection first using add_collection(). Existing collection are: %s' % (collection, self._collections))

        return self._db[str(collection)]

    @ensure_connection
    def _add_collection(self, collection: str):
        """
        |decorated| :any:`ensure_connection`

        Add a collection to the database.

        :type collection: str
        :param collection: Collection name to add
        """
        self._db.create_collection(str(collection))
