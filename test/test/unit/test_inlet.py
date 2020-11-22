import asyncio
import threading
from unittest import TestCase

from unittest.mock import MagicMock

from databay import Inlet, Record


class DummyInlet(Inlet):
    def __init__(self, array=True, raw=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.array = array
        self.raw = raw
        self.data = {'test': 10}
        self.record = self.new_record(self.data)

    def pull(self, update):
        rv = self.data
        if not self.raw:
            rv = self.record
        if self.array:
            rv = [rv]

        return rv

class DummyAsyncInlet(DummyInlet):
    async def pull(self, update):
        return super().pull(update)

class DummyMultiInlet(DummyInlet):
    async def pull(self, update):
        a = super().pull(update)
        b = super().pull(update)
        c = super().pull(update)
        return [a, b, c]

class DummyStartShutdownInlet(DummyInlet):
    start_called = False
    shutdown_called = False

    def on_start(self):
        self.start_called = True

    def on_shutdown(self):
        self.shutdown_called = True

def sync_async(array, raw):
    def fn_wrapper(fn):
        def wrapper(test_kls):
            def run_with(inlet):
                with test_kls.subTest(msg=f"Inlet {inlet}"):
                    fn(test_kls, inlet)
            run_with(DummyInlet(array=array, raw=raw))
            run_with(DummyAsyncInlet(array=array, raw=raw))
        return wrapper
    return fn_wrapper

class TestInlet(TestCase):


    @sync_async(array=False, raw=True)
    def test_pull_raw(self, inlet):
        # inlet = DummyInlet(array=False, raw=True)
        rv = asyncio.run(inlet._pull(None))
        self.assertIsInstance(rv, list, 'Should wrap data in an array')
        self.assertIsInstance(rv[0], Record, 'Should wrap data in records')

    @sync_async(array=False, raw=False)
    def test_pull_record(self, inlet):
        # inlet = DummyInlet(array=False, raw=False)
        rv = asyncio.run(inlet._pull(None))
        self.assertIsInstance(rv, list, 'Should wrap data in an array')
        self.assertIsInstance(rv[0], Record, 'Should return a record')
        self.assertEqual(rv[0], inlet.record, 'Record returned should be same as inlet\'s')

    @sync_async(array=True, raw=True)
    def test_pull_raw_array(self, inlet):
        # inlet = DummyInlet(array=True, raw=True)
        rv = asyncio.run(inlet._pull(None))
        self.assertIsInstance(rv, list, 'Should return an array')
        self.assertIsInstance(rv[0], Record, 'Should wrap data in records')

    @sync_async(array=True, raw=False)
    def test_pull_record_array(self, inlet):
        # inlet = DummyInlet(array=True, raw=False)
        rv = asyncio.run(inlet._pull(None))
        self.assertIsInstance(rv, list, 'Should return an array')
        self.assertIsInstance(rv[0], Record, 'Should return a record')
        self.assertEqual(rv[0], inlet.record, 'Record returned should be same as inlet\'s')

    def test_pull_multiple_raw(self):
        inlet = DummyMultiInlet(array=True, raw=True)
        rv = asyncio.run(inlet._pull(None))
        self.assertIsInstance(rv, list, 'Should return an array')
        self.assertIsInstance(rv[0], Record, 'Should return a record')
        self.assertEqual(len(rv), 3, 'Should return 3 records')

    def test_pull_multiple_records(self):
        inlet = DummyMultiInlet(array=True, raw=False)
        rv = asyncio.run(inlet._pull(None))
        self.assertIsInstance(rv, list, 'Should return an array')
        self.assertIsInstance(rv[0], Record, 'Should return a record')
        self.assertEqual(len(rv), 3, 'Should return 3 records')


    def test_try_start(self):
        inlet = DummyStartShutdownInlet()
        inlet.try_start()
        self.assertTrue(inlet.active)
        self.assertTrue(inlet.start_called)
        self.assertFalse(inlet.shutdown_called)

    def test_try_shutdown(self):
        inlet = DummyStartShutdownInlet()
        inlet._active = True
        inlet.try_shutdown()
        self.assertFalse(inlet.active)
        self.assertTrue(inlet.shutdown_called)
        self.assertFalse(inlet.start_called)

    def test_try_start_already_active(self):
        inlet = DummyStartShutdownInlet()
        inlet._active = True
        inlet.try_start()
        self.assertTrue(inlet.active)
        self.assertFalse(inlet.start_called)
        self.assertFalse(inlet.shutdown_called)

    def test_try_shutdown_already_inactive(self):
        inlet = DummyStartShutdownInlet()
        inlet.try_shutdown()
        self.assertFalse(inlet.active)
        self.assertFalse(inlet.shutdown_called)
        self.assertFalse(inlet.start_called)

    def test_try_start_multiple(self):
        inlet = DummyStartShutdownInlet()
        inlet.try_start()
        self.assertTrue(inlet.active)
        self.assertTrue(inlet.start_called)
        self.assertFalse(inlet.shutdown_called)
        inlet.try_start()
        self.assertTrue(inlet.active)
        self.assertTrue(inlet.start_called)
        self.assertFalse(inlet.shutdown_called)

    def test_try_shutdown_multiple(self):
        inlet = DummyStartShutdownInlet()
        inlet._active = True
        inlet.try_shutdown()
        self.assertFalse(inlet.active)
        self.assertTrue(inlet.shutdown_called)
        self.assertFalse(inlet.start_called)
        inlet.try_shutdown()
        self.assertFalse(inlet.active)
        self.assertTrue(inlet.shutdown_called)
        self.assertFalse(inlet.start_called)


    """ This isn't easy to test properly, as race condition rarely happens. Add time.sleep(0.1) 
    to Inlet.try_start before changing self._active to generate race condition - then the _thread_lock 
    should indeed prevent it."""
    def test_try_start_race_condition(self):
        inlet = DummyStartShutdownInlet()
        inlet.on_start = MagicMock()

        def worker(event):
            event.wait()
            inlet.try_start()

        ev = threading.Event()
        threads = []
        for i in range (0, 10):
            t = threading.Thread(target=worker, daemon=True, args=[ev])
            threads.append(t)
            t.start()

        ev.set()
        for t in threads:
            t.join()
        inlet.on_start.assert_called_once()

    # Read test_try_start_race_condition
    def test_try_shutdown_race_condition(self):
        inlet = DummyStartShutdownInlet()
        inlet._active = True
        inlet.on_shutdown = MagicMock()

        def worker(event):
            event.wait()
            inlet.try_shutdown()

        ev = threading.Event()
        threads = []
        for i in range (0, 10):
            t = threading.Thread(target=worker, daemon=True, args=[ev])
            threads.append(t)
            t.start()

        ev.set()
        for t in threads:
            t.join()
        inlet.on_shutdown.assert_called_once()
