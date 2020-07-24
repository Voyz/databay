import asyncio
import unittest
from unittest import TestCase
from unittest.mock import patch

from databay import Record, Update
from test_utils import fqname


class InletTester(TestCase):

    def get_inlet(self):
        raise NotImplementedError()

    def setUp(self):
        self.gmetadata = {'global':'global'}
        self.inlet = self.get_inlet()
        self.inlet._metadata = {**self.inlet._metadata, **self.gmetadata}

    def test_new_record(self):
        payload = {'test':123}
        metadata = {'metadata':321}
        record = self.inlet.new_record(payload=payload, metadata=metadata)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.payload, payload)
        self.assertLessEqual(metadata.items(), record.metadata.items(), 'Local metadata should be contained in record.metadata')
        self.assertLessEqual(self.gmetadata.items(), record.metadata.items(), 'Global metadata should be contained in record.metadata')

    def test_new_record_override_global(self):
        payload = {'test':123}
        metadata = {'global':'local'}
        record = self.inlet.new_record(payload=payload, metadata=metadata)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.payload, payload)
        self.assertLessEqual(metadata.items(), record.metadata.items(), 'Local metadata should be contained in record.metadata')
        self.assertEqual(record.metadata['global'], 'local', 'Global metadata should be overridden by local metadata')

    @patch(fqname(Update))
    def test_pull(self, update):
        records = asyncio.run(self.inlet._pull(update))

        self.assertIsInstance(records, (list, tuple))
        for record in records:
            self.assertIsInstance(record, Record)
            self.assertIsNotNone(record.payload)
            self.assertLessEqual(self.gmetadata.items(), record.metadata.items(),
                                 'Global metadata should be contained in record.metadata')




