import asyncio
import logging
import time
from datetime import timedelta, datetime
from unittest import TestCase, mock

from databay.errors import ImplementationError
from databay.inlet import Inlet
from databay.link import Link
from databay.outlet import Outlet


class DummyInlet(Inlet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.record = self.new_record({'test': 10})

    async def pull(self, count):
        return [self.record]

class DummyOutlet(Outlet):
    async def push(self, records, count):
        self.records = records

class DummyInletInvalid(Inlet):
    def pull(self, count):
        return [None]

class DummyOutletInvalid(Outlet):
    def push(self, records, count):
        self.records = records

class DummyAwaitInlet(Inlet):
    def __init__(self, asynchronous:bool=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.record = self.new_record({'test': 10})
        self.asynchronous = asynchronous
        self.wait_time = 0.01

    async def pull(self, count):
        if self.asynchronous:
            await asyncio.sleep(self.wait_time)
        else:
            time.sleep(self.wait_time)
        return [self.record]

class TestLink(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.getLogger('databay').setLevel(logging.WARNING)

    def test_update_single(self):
        inlet1 = DummyInlet()
        outlet1 = DummyOutlet()
        link = Link([inlet1], [outlet1], timedelta(seconds=1), copy_records=False)

        link.transfer()

        self.assertEqual(outlet1.records[0], inlet1.record)

    def test_update_multiple(self):
        inlet1 = DummyInlet()
        inlet2 = DummyInlet()
        outlet1 = DummyOutlet()
        outlet2 = DummyOutlet()
        link = Link([inlet1, inlet2], [outlet1, outlet2], timedelta(seconds=1), copy_records=False)

        link.transfer()

        self.assertEqual(outlet1.records, [inlet1.record, inlet2.record])
        self.assertEqual(outlet2.records, [inlet1.record, inlet2.record])


    def test_metadata_global(self):
        inlet1 = DummyInlet(metadata={'secret': 'global'})
        outlet1 = DummyOutlet()
        link = Link([inlet1], [outlet1], timedelta(seconds=1))

        link.transfer()

        self.assertEqual(outlet1.records[0].metadata['secret'], inlet1.metadata['secret'])

    # test if overriding global metadata with local metadata works
    def test_metadata_local(self):
        inlet1 = DummyInlet(metadata={'secret': 'global'})
        inlet1.record = inlet1.new_record({'test':20}, metadata={'secret':'local', 'key':'value'})
        outlet1 = DummyOutlet()
        link = Link([inlet1], [outlet1], timedelta(seconds=1))

        link.transfer()

        self.assertEqual(outlet1.records[0].metadata['secret'], inlet1.record.metadata['secret'])
        self.assertEqual(outlet1.records[0].metadata['key'], inlet1.record.metadata['key'])
        self.assertNotEqual(outlet1.records[0].metadata['secret'], inlet1.metadata['secret'])



    def test_await_pull_single(self):
        inlet1 = DummyAwaitInlet()
        outlet1 = DummyOutlet()
        link = Link([inlet1], [outlet1], timedelta(seconds=1), copy_records=False)

        link.transfer()

        self.assertEqual(outlet1.records[0], inlet1.record)

    # test if asynchronous calls indeed run in parallel
    def test_await_pull_multiple_async(self):
        inlet1 = DummyAwaitInlet()
        inlet2 = DummyAwaitInlet()
        inlet3 = DummyAwaitInlet()
        outlet1 = DummyOutlet()
        link = Link([inlet1, inlet2, inlet3], [outlet1], timedelta(seconds=1), copy_records=False)

        start_time = datetime.now()

        link.transfer()

        end_time = datetime.now()
        diff = end_time - start_time

        self.assertEqual(outlet1.records, [inlet1.record, inlet2.record, inlet3.record])
        total_wait_time = inlet1.wait_time + inlet2.wait_time + inlet3.wait_time
        self.assertLess(diff.total_seconds(), total_wait_time)

    # test if synchronous calls indeed run synchronously
    def test_await_pull_multiple_sync(self):
        inlet1 = DummyAwaitInlet(False)
        inlet2 = DummyAwaitInlet(False)
        inlet3 = DummyAwaitInlet(False)
        outlet1 = DummyOutlet()
        link = Link([inlet1, inlet2, inlet3], [outlet1], timedelta(seconds=0.), copy_records=False)

        start_time = datetime.now()

        link.transfer()

        end_time = datetime.now()
        diff = end_time - start_time

        self.assertEqual(outlet1.records, [inlet1.record, inlet2.record, inlet3.record])
        total_wait_time = inlet1.wait_time + inlet2.wait_time + inlet3.wait_time
        self.assertGreaterEqual(diff.total_seconds(), total_wait_time)



    def test_on_start(self):
        inlet1 = DummyInlet()
        outlet1 = DummyOutlet()
        link = Link([inlet1], [outlet1], timedelta(seconds=1))

        self.assertFalse(inlet1.active)
        self.assertFalse(outlet1.active)
        link.on_start()
        self.assertTrue(inlet1.active)
        self.assertTrue(outlet1.active)

    def test_on_start_already_active(self):
        inlet1 = DummyInlet()
        outlet1 = DummyOutlet()
        inlet1.on_start = mock.Mock()
        outlet1.on_start = mock.Mock()
        inlet1._active = True
        outlet1._active = True
        link = Link([inlet1], [outlet1], timedelta(seconds=1))

        link.on_start()

        inlet1.on_start.assert_not_called()
        outlet1.on_start.assert_not_called()

    def test_on_shutdown(self):
        inlet1 = DummyInlet()
        outlet1 = DummyOutlet()
        inlet1._active = True
        outlet1._active = True

        link = Link(inlet1, outlet1, timedelta(seconds=1))

        self.assertTrue(inlet1.active)
        self.assertTrue(outlet1.active)
        link.on_shutdown()
        self.assertFalse(inlet1.active)
        self.assertFalse(outlet1.active)

    def test_on_shutdown_already_inactive(self):
        inlet1 = DummyInlet()
        outlet1 = DummyOutlet()
        inlet1.on_shutdown = mock.Mock()
        outlet1.on_shutdown = mock.Mock()
        link = Link([inlet1], [outlet1], timedelta(seconds=1))

        link.on_shutdown()

        inlet1.on_shutdown.assert_not_called()
        outlet1.on_shutdown.assert_not_called()

    # def test_inlet_invalid(self):
    #     self.assertRaises(ImplementationError, DummyInletInvalid)
    #
    #
    # def test_outlet_invalid(self):
    #     self.assertRaises(ImplementationError, DummyOutletInvalid)
