import asyncio
import copy
import io
import os
from unittest import TestCase

from unittest.mock import patch

from databay import Record, Update
from databay.outlets import PrintOutlet
from databay.outlets.file_outlet import FileOutlet
from test_utils import fqname


class TestFileOutlet(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.this_filepath = os.path.abspath(os.path.dirname(__file__))
        cls.target_filepath = os.path.join(cls.this_filepath, 'data/_file_outlet_target.txt')
        cls.attempt_filepath = os.path.join(cls.this_filepath, 'data/_file_outlet_attempt.txt')
        cls.custom_filepath = os.path.join(cls.this_filepath, 'data/_file_outlet_custom_attempt.txt')
        with open(cls.target_filepath, 'r') as f:
            cls.target = f.read()

    @patch(fqname(Record), spec=Record)
    @patch(fqname(Update), spec=Update)
    def setUp(self, update, record):
        if os.path.exists(self.attempt_filepath):
            os.remove(self.attempt_filepath)

        if os.path.exists(self.custom_filepath):
            os.remove(self.custom_filepath)

        self.file_outlet = FileOutlet(self.attempt_filepath)
        self.update = update
        self.record = record

        record.payload = 'test'
        record.metadata = {}

        record.__repr__ = lambda x: 'TestRecord(test)'
        update.__repr__ = lambda x: 'TestUpdate()'

        self.records = [copy.copy(record) for i in range(0,4)]

    def test_push_append_mode(self):
        asyncio.run(self.file_outlet._push(self.records, self.update))

        self.assertTrue(os.path.exists(self.attempt_filepath), 'File should exist')

        with open(self.attempt_filepath, 'r') as f:
            self.assertEqual(f.read(), self.target)

        os.remove(self.attempt_filepath)

    def test_push_write_mode(self):

        for record in self.records:
            record.metadata = {FileOutlet.FILE_MODE: 'w'}

        asyncio.run(self.file_outlet._push(self.records, self.update))

        self.assertTrue(os.path.exists(self.attempt_filepath), 'File should exist')

        with open(self.attempt_filepath, 'r') as f:
            self.assertEqual(f.read(), 'test\n', 'Each write should have overridden the previous.')

        os.remove(self.attempt_filepath)

    def test_push_custom_files(self):
        self.records[0].metadata = {FileOutlet.FILEPATH: self.custom_filepath}

        asyncio.run(self.file_outlet._push(self.records, self.update))

        self.assertTrue(os.path.exists(self.attempt_filepath), 'File should exist')
        self.assertTrue(os.path.exists(self.custom_filepath), 'File should exist')

        with open(self.attempt_filepath, 'r') as f:
            self.assertEqual(f.read(), 'test\ntest\ntest\n', 'Should miss one record')

        with open(self.custom_filepath, 'r') as f:
            self.assertEqual(f.read(), 'test\n', 'Should contain the one record')

        os.remove(self.attempt_filepath)
        os.remove(self.custom_filepath)

