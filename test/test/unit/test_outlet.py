import asyncio
import threading
from unittest import TestCase, mock
from unittest.mock import MagicMock


from databay import Outlet, Record, Update


class DummyOutlet(Outlet):
    def push(self, records, update):
        self.records = records


class DummyAsyncOutlet(DummyOutlet):
    async def push(self, records, update):
        self.records = records


class DummyStartShutdownOutlet(DummyOutlet):
    start_called = False
    shutdown_called = False

    def on_start(self):
        self.start_called = True

    def on_shutdown(self):
        self.shutdown_called = True

update_mock = MagicMock(spec=Update)

class TestOutlet(TestCase):

    def test_push(self):
        outlet = DummyOutlet()
        records = [Record(None), Record(None)]
        asyncio.run(outlet._push(records, update_mock))

        self.assertEqual(outlet.records, records)

    def test_push_async(self):
        outlet = DummyAsyncOutlet()
        records = [Record(None), Record(None)]
        asyncio.run(outlet._push(records, update_mock))

        self.assertEqual(outlet.records, records)

    def test_try_start(self):
        outlet = DummyStartShutdownOutlet()
        outlet.try_start()
        self.assertTrue(outlet.active)
        self.assertTrue(outlet.start_called)
        self.assertFalse(outlet.shutdown_called)

    def test_try_shutdown(self):
        outlet = DummyStartShutdownOutlet()
        outlet._active = True
        outlet.try_shutdown()
        self.assertFalse(outlet.active)
        self.assertTrue(outlet.shutdown_called)
        self.assertFalse(outlet.start_called)

    def test_try_start_already_active(self):
        outlet = DummyStartShutdownOutlet()
        outlet._active = True
        outlet.try_start()
        self.assertTrue(outlet.active)
        self.assertFalse(outlet.start_called)
        self.assertFalse(outlet.shutdown_called)

    def test_try_shutdown_already_inactive(self):
        outlet = DummyStartShutdownOutlet()
        outlet.try_shutdown()
        self.assertFalse(outlet.active)
        self.assertFalse(outlet.shutdown_called)
        self.assertFalse(outlet.start_called)

    def test_try_start_multiple(self):
        outlet = DummyStartShutdownOutlet()
        outlet.try_start()
        self.assertTrue(outlet.active)
        self.assertTrue(outlet.start_called)
        self.assertFalse(outlet.shutdown_called)
        outlet.try_start()
        self.assertTrue(outlet.active)
        self.assertTrue(outlet.start_called)
        self.assertFalse(outlet.shutdown_called)

    def test_try_shutdown_multiple(self):
        outlet = DummyStartShutdownOutlet()
        outlet._active = True
        outlet.try_shutdown()
        self.assertFalse(outlet.active)
        self.assertTrue(outlet.shutdown_called)
        self.assertFalse(outlet.start_called)
        outlet.try_shutdown()
        self.assertFalse(outlet.active)
        self.assertTrue(outlet.shutdown_called)
        self.assertFalse(outlet.start_called)

    """ This isn't easy to test properly, as race condition rarely happens. Add time.sleep(0.1) 
    to Outlet.try_start before changing self._active to generate race condition - then the _thread_lock 
    should indeed prevent it."""

    def test_try_start_race_condition(self):
        outlet = DummyStartShutdownOutlet()
        outlet.on_start = MagicMock()

        def worker(event):
            event.wait()
            outlet.try_start()

        ev = threading.Event()
        threads = []
        for i in range(0, 10):
            t = threading.Thread(target=worker, daemon=True, args=[ev])
            threads.append(t)
            t.start()

        ev.set()
        for t in threads:
            t.join()
        outlet.on_start.assert_called_once()

    # Read test_try_start_race_condition
    def test_try_shutdown_race_condition(self):
        outlet = DummyStartShutdownOutlet()
        outlet._active = True
        outlet.on_shutdown = MagicMock()

        def worker(event):
            event.wait()
            outlet.try_shutdown()

        ev = threading.Event()
        threads = []
        for i in range(0, 10):
            t = threading.Thread(target=worker, daemon=True, args=[ev])
            threads.append(t)
            t.start()

        ev.set()
        for t in threads:
            t.join()
        outlet.on_shutdown.assert_called_once()

    def test_processors_one(self):
        payload = [2, 3]
        records = [Record(payload=p) for p in payload]
        processor = MagicMock(side_effect = lambda r: r)
        outlet = DummyOutlet(processors = processor)
        asyncio.run(outlet._push(records, update_mock))
        processor.assert_called_with(records)

    def test_processors_many(self):
        payload = [2, 3]
        records = [Record(payload=p) for p in payload]
        processorA = MagicMock(side_effect = lambda x: x)
        processorB = MagicMock(side_effect = lambda x: x)
        outlet = DummyOutlet(processors = [processorA, processorB])
        asyncio.run(outlet._push(records, update_mock))
        processorA.assert_called_with(records)
        processorB.assert_called_with(records)

    def test_processors_change_records(self):
        records = [2, 3]
        processorA = MagicMock(side_effect = lambda r: list(map(lambda y: y*y, r)))
        processorB = MagicMock(side_effect = lambda r: list(map(lambda y: -y, r)))

        outlet = DummyOutlet(processors = [processorA, processorB])
        outlet.push = MagicMock()
        asyncio.run(outlet._push(records, update_mock))
        processorA.assert_called_with(records)
        processorB.assert_called_with([4, 9])
        outlet.push.assert_called_with([-4, -9], mock.ANY)

    def test_processors_filter_records(self):
        records = [2, 3, 4]
        processorA = MagicMock(side_effect = lambda r: list(filter(lambda y: y>2, r)))
        processorB = MagicMock(side_effect = lambda r: list(filter(lambda y: y%2==0, r)))

        outlet = DummyOutlet(processors = [processorA, processorB])
        outlet.push = MagicMock()
        asyncio.run(outlet._push(records, update_mock))
        processorA.assert_called_with(records)
        processorB.assert_called_with([3, 4])
        outlet.push.assert_called_with([4], mock.ANY)



