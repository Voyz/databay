from unittest import TestCase

import mongomock
from config_test import patch, MagicMock
from mongomock import Collection

from databay import Record, Update
from databay.outlets import MongoOutlet
from databay.outlets.mongo_outlet import MongoCollectionNotFound, ensure_connection
from test_utils import fqname

class TestMongoOutlet(TestCase):

    def setUp(self):
        self.outlet = MongoOutlet()

    @mongomock.patch(servers=(('localhost', 27017),))
    def test_connect(self):

        result = self.outlet.connect()

        self.assertFalse(result)
        self.assertEqual(self.outlet._db.name, 'databay')
        self.assertEqual(self.outlet._client.address[0], 'localhost')
        self.assertEqual(self.outlet._client.address[1], 27017)

    @mongomock.patch(servers=(('test', 1234),))
    def test_connect_custom_host(self):
        self.outlet = MongoOutlet(host='test', port=1234)

        self.outlet.connect()

        self.assertEqual(self.outlet._client.host, 'test')
        self.assertEqual(self.outlet._client.port, 1234)

    @mongomock.patch(servers=(('localhost', 27017),))
    def test_connect_custom_database(self):
        result = self.outlet.connect('my_database')

        self.assertFalse(result)
        self.assertEqual(self.outlet._db.name, 'my_database')

    @mongomock.patch(servers=(('localhost', 27017),))
    def test_connect_twice_same(self):
        result = self.outlet.connect()
        self.assertFalse(result)
        result = self.outlet.connect()
        self.assertTrue(result)
        self.assertEqual(self.outlet._db.name, 'databay')
        self.assertEqual(self.outlet._client.address[0], 'localhost')
        self.assertEqual(self.outlet._client.address[1], 27017)

    @mongomock.patch(servers=(('localhost', 27017),))
    def test_connect_twice_different(self):
        result = self.outlet.connect()
        self.assertFalse(result)
        self.assertEqual(self.outlet._db.name, 'databay')

        result = self.outlet.connect('test')
        self.assertFalse(result)
        self.assertEqual(self.outlet._db.name, 'test')
        self.assertEqual(self.outlet._client.address[0], 'localhost')
        self.assertEqual(self.outlet._client.address[1], 27017)

    def test_disconnect(self):
        close_mock = MagicMock()
        self.outlet._client = MagicMock(close=close_mock)
        self.outlet._db = MagicMock()
        self.outlet.disconnect()

        close_mock.assert_called_once()
        self.assertIsNone(self.outlet._client)
        self.assertIsNone(self.outlet._db)

    def test_on_start(self):
        self.outlet.connect = MagicMock()
        self.outlet.on_start()
        self.outlet.connect.assert_called_once()

    def test_on_shutdown(self):
        self.outlet.disconnect = MagicMock()
        self.outlet.on_shutdown()
        self.outlet.disconnect.assert_called_once()

    @mongomock.patch(servers=(('localhost', 27017),))
    def test__add_collection(self):
        name = 'test_collection'
        self.outlet._add_collection(name)
        self.assertTrue(name in self.outlet._db.list_collection_names(), f'Database should contain collection \'{name}\'')
        self.assertIsInstance(self.outlet._db[name], Collection)


    @mongomock.patch(servers=(('localhost', 27017),))
    def test__add_collection_invalid(self):
        name = 'test_collection'
        self.outlet._add_collection(None)
        self.assertFalse(name in self.outlet._db.list_collection_names(), f'Database should not contain collection \'{name}\'')

    @mongomock.patch(servers=(('localhost', 27017),))
    def test__get_collection(self):
        name = 'test_collection'
        self.outlet._add_collection(name)
        self.assertTrue(name in self.outlet._db.list_collection_names(), f'Database should contain collection \'{name}\'')
        self.assertIsInstance(self.outlet._db[name], Collection)

        collection = self.outlet._get_collection(name)
        self.assertIsInstance(collection, Collection)

    @mongomock.patch(servers=(('localhost', 27017),))
    def test__get_collection_invalid(self):
        name = 'test_collection'
        self.outlet._add_collection(name)
        self.assertTrue(name in self.outlet._db.list_collection_names(), f'Database should contain collection \'{name}\'')
        self.assertIsInstance(self.outlet._db[name], Collection)

        self.assertRaises(MongoCollectionNotFound, self.outlet._get_collection, 'invalid_name')

    @mongomock.patch(servers=(('localhost', 27017),))
    @patch(fqname(Record), spec=Record)
    @patch(fqname(Record), spec=Record)
    @patch(fqname(Record), spec=Record)
    def test__group_by_collection(self, recordA, recordB, recordB2):
        recordA.metadata = {MongoOutlet.MONGODB_COLLECTION: 'A'}
        recordB.metadata = {MongoOutlet.MONGODB_COLLECTION: 'B'}
        recordB2.metadata = {MongoOutlet.MONGODB_COLLECTION: 'B'}
        recordA.payload = 'testA'
        recordB.payload = 'testB'
        recordB2.payload = 'testB2'

        target = {'A': ['testA'], 'B': ['testB', 'testB2']}

        records = [recordA, recordB, recordB2]

        collections = self.outlet._group_by_collection(records)
        self.assertEqual(collections.keys(), target.keys())
        self.assertEqual(collections['A'], [recordA.payload])
        self.assertEqual(collections['B'], [recordB.payload, recordB2.payload])

    @mongomock.patch(servers=(('localhost', 27017),))
    @patch(fqname(Record), spec=Record)
    @patch(fqname(Record), spec=Record)
    def test__group_by_collection_list_payload(self, recordA, recordB):
        recordA.metadata = {MongoOutlet.MONGODB_COLLECTION: 'A'}
        recordB.metadata = {MongoOutlet.MONGODB_COLLECTION: 'B'}
        recordA.payload = 'testA'
        recordB.payload = ['testB', 'testB2']

        target = {'A': ['testA'], 'B': ['testB', 'testB2']}

        records = [recordA, recordB]

        collections = self.outlet._group_by_collection(records)
        self.assertEqual(collections.keys(), target.keys())
        self.assertEqual(collections['A'], [recordA.payload])
        self.assertEqual(collections['B'], [*recordB.payload])


    @mongomock.patch(servers=(('localhost', 27017),))
    @patch(fqname(Update), spec=Update)
    @patch(fqname(Record), spec=Record)
    @patch(fqname(Record), spec=Record)
    def test_push(self, recordA, recordB, update):
        # recordA = Record(1)
        # recordB = Record(1)
        recordA.metadata = {MongoOutlet.MONGODB_COLLECTION: 'A'}
        recordB.metadata = {MongoOutlet.MONGODB_COLLECTION: 'B'}
        recordA.payload = {'testA':1}
        recordB.payload = [{'testB':2}, {'testB2':3}]


        records = [recordA, recordB]
        self.outlet.try_start()
        self.outlet.push(records, update)


        for record in records:
            collection = self.outlet._get_collection(record.metadata.get(MongoOutlet.MONGODB_COLLECTION))
            payload = record.payload
            if not isinstance(payload, list):
                payload = [payload]

            for p in payload:
                result = collection.find_one({'_id': p.get('_id')})
                self.assertEqual(p, result)

        self.outlet.try_shutdown()

    @mongomock.patch(servers=(('localhost', 27017),))
    @patch(fqname(Update), spec=Update)
    @patch(fqname(Record), spec=Record)
    def test_push_inactive(self, record, update):
        result = self.outlet.push([record], update)
        self.assertFalse(result, 'Push should have stopped and returned False')

    @mongomock.patch(servers=(('localhost', 27017),))
    def test_ensure_connection(self):
        mock = MagicMock(foo=MagicMock(), _db=None)

        ensure_connection(mock.foo)(mock)

        mock.connect.assert_called_once()
        mock.foo.assert_called_once()

