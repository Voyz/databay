import io
import unittest

from asynctest import TestCase, patch, asyncio

from databay import Record, Update
from databay.outlets import PrintOutlet
from test_utils import fqname


class TestPrintOutlet(TestCase):

    @patch(fqname(Record), spec=Record)
    @patch(fqname(Update), spec=Update)
    def setUp(self, update, record):
        self.print_outlet = PrintOutlet()
        self.update = update
        self.record = record

        record.payload = 'test'
        record.metadata.return_value = {}

        record.__repr__ = lambda x: 'TestRecord(test)'
        update.__repr__ = lambda x: 'TestUpdate()'

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_push(self, stdout):

        asyncio.run(self.print_outlet._push([self.record], self.update))

        self.assertEqual(stdout.getvalue(), 'TestUpdate() TestRecord(test)\n')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_push_only_payload(self, stdout):
        self.print_outlet.only_payload = True

        asyncio.run(self.print_outlet._push([self.record], self.update))

        self.assertEqual(stdout.getvalue(), 'TestUpdate() test\n')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_push_skip_update(self, stdout):
        self.print_outlet.skip_update = True

        asyncio.run(self.print_outlet._push([self.record], self.update))

        self.assertEqual(stdout.getvalue(), 'TestRecord(test)\n')


if __name__ == '__main__':
    unittest.main()
