import copy
import io
import os

from asynctest import TestCase, patch, asyncio

from databay import Record, Update
from databay.outlets import PrintOutlet
from databay.outlets.csv_outlet import CsvOutlet
from test_utils import fqname


class TestCsvOutlet(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.this_filepath = os.path.abspath(os.path.dirname(__file__))
        cls.target_filepath = os.path.join(cls.this_filepath, 'data/_csv_outlet_target.csv')
        cls.attempt_filepath = os.path.join(cls.this_filepath, 'data/_csv_outlet_attempt.csv')
        cls.custom_filepath = os.path.join(cls.this_filepath, 'data/_csv_outlet_custom_attempt.csv')
        with open(cls.target_filepath, 'r') as f:
            cls.target = f.read()

    @patch(fqname(Record), spec=Record)
    @patch(fqname(Update), spec=Update)
    def setUp(self, update, record):
        if os.path.exists(self.attempt_filepath):
            os.remove(self.attempt_filepath)

        if os.path.exists(self.custom_filepath):
            os.remove(self.custom_filepath)

        self.csv_outlet = CsvOutlet(self.attempt_filepath)
        self.update = update
        self.record = record

        record.payload = {'foo': 'bar', 'baz': 'qux'}
        record.metadata = {}

        record.__repr__ = lambda x: 'TestRecord(test)'
        update.__repr__ = lambda x: 'TestUpdate()'

        self.records = [copy.copy(record) for i in range(0,4)]

    def test_push_append_mode(self):
        asyncio.run(self.csv_outlet._push(self.records, self.update))

        self.assertTrue(os.path.exists(self.attempt_filepath), 'File should exist')

        with open(self.attempt_filepath, 'r') as f:
            self.assertEqual(f.read(), self.target)

        os.remove(self.attempt_filepath)

    def test_push_write_mode(self):

        for record in self.records:
            record.metadata = {CsvOutlet.FILE_MODE: 'w'}

        asyncio.run(self.csv_outlet._push(self.records, self.update))

        self.assertTrue(os.path.exists(self.attempt_filepath), 'File should exist')

        with open(self.attempt_filepath, 'r') as f:
            self.assertEqual(f.read(), 'foo,baz\nbar,qux\n', 'Each write should have overridden the previous.')

        os.remove(self.attempt_filepath)

    def test_push_custom_files(self):
        self.records[0].metadata = {CsvOutlet.CSV_FILE: self.custom_filepath}

        asyncio.run(self.csv_outlet._push(self.records, self.update))

        self.assertTrue(os.path.exists(self.attempt_filepath), 'File should exist')
        self.assertTrue(os.path.exists(self.custom_filepath), 'File should exist')

        with open(self.attempt_filepath, 'r') as f:
            self.assertEqual(f.read(), 'foo,baz\nbar,qux\nbar,qux\nbar,qux\n', 'Should miss one record')

        with open(self.custom_filepath, 'r') as f:
            self.assertEqual(f.read(), 'foo,baz\nbar,qux\n', 'Should contain the one record')

        os.remove(self.attempt_filepath)
        os.remove(self.custom_filepath)

