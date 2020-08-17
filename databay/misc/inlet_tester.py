import asyncio
import functools
import unittest
from unittest import TestCase
from unittest.mock import patch

from asynctest import mock

from databay import Record, Update
from databay.inlets import NullInlet
from test_utils import fqname


def for_each_inlet(fn):
    """Runs the test for each inlet returned from :any:`InletTester.get_inlet`"""

    # @functools.wraps(fn)
    def wrapper(test_kls, *args, **kwargs):
        for inlet in test_kls.inlets:
            inlet._metadata = {**test_kls.inlet._metadata, **test_kls.gmetadata}
            test_kls.inlet = inlet
            with test_kls.subTest(msg=f"Inlet {str(inlet)}"):
                fn(test_kls, *args, **kwargs)

    return wrapper

class InletTester(TestCase):
    """
    Utility class used for testing concrete implementations of :any:`Inlet`.
    """

    def get_inlet(self): # pragma: no cover
        """Implement this method to return instances of your inlet class."""
        return NullInlet()

    def setUp(self):
        self.gmetadata = {'global':'global'}
        self.inlets = self.get_inlet()
        if not isinstance(self.inlets, list):
            self.inlets = [self.inlets]

        self.inlet = self.inlets[0]
        self.inlet._metadata = {**self.inlet._metadata, **self.gmetadata}

    @for_each_inlet
    def test_new_record(self):
        """
        |decorated| :any:`for_each_inlet`

        Test creating new records and passing local metadata.
        """
        payload = {'test':123}
        metadata = {'metadata':321}
        record = self.inlet.new_record(payload=payload, metadata=metadata)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.payload, payload)
        self.assertLessEqual(metadata.items(), record.metadata.items(), 'Local metadata should be contained in record.metadata')
        self.assertLessEqual(self.gmetadata.items(), record.metadata.items(), 'Global metadata should be contained in record.metadata')

    @for_each_inlet
    def test_new_record_override_global(self):
        """
        |decorated| :any:`for_each_inlet`

        Test creating new records and overriding global metadata.
        """
        payload = {'test':123}
        metadata = {'global':'local'}
        record = self.inlet.new_record(payload=payload, metadata=metadata)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.payload, payload)
        self.assertLessEqual(metadata.items(), record.metadata.items(), 'Local metadata should be contained in record.metadata')
        self.assertEqual(record.metadata['global'], 'local', 'Global metadata should be overridden by local metadata')

    @patch(fqname(Update))
    @for_each_inlet
    def test_dont_read_metadata(self, update):
        """
        |decorated| :any:`for_each_inlet`

        Test creating new records and overriding global metadata.
        """

        meta = mock.MagicMock()
        meta.keys.return_value = self.gmetadata.keys()
        meta.__getitem__.side_effect = lambda x: self.gmetadata.__getitem__(x)

        self.inlet._metadata = meta
        self.inlet.on_start()
        records = asyncio.run(self.inlet._pull(update))
        self.inlet.on_shutdown()
        self.inlet._metadata.get.assert_not_called()
        self.assertEqual(self.inlet._metadata.__getitem__.call_count, len(self.gmetadata))

        self.assertIsInstance(records, (list))
        for record in records:
            self.assertIsInstance(record, Record)
            self.assertIsNotNone(record.payload)
            self.assertLessEqual(self.gmetadata.items(), record.metadata.items(),
                                 'Global metadata should be contained in record.metadata')


    @for_each_inlet
    @patch(fqname(Update))
    def test_pull(self, update):
        """
        |decorated| :any:`for_each_inlet`

        Test pulling data from the inlet.
        """
        self.inlet.on_start()
        records = asyncio.run(self.inlet._pull(update))
        self.inlet.on_shutdown()

        self.assertIsInstance(records, (list))
        for record in records:
            self.assertIsInstance(record, Record)
            self.assertIsNotNone(record.payload)
            self.assertLessEqual(self.gmetadata.items(), record.metadata.items(),
                                 'Global metadata should be contained in record.metadata')




