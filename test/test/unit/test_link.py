import asyncio
import logging
from asyncio import Future
from datetime import timedelta
from unittest import TestCase, mock
from unittest.mock import MagicMock, patch, call

import databay
from databay import Inlet, Outlet
from databay.errors import InvalidNodeError
from databay.link import Link
from test_utils import DummyException, fqname


# monkey patch the MagicMock's await
async def async_magic():
    pass
MagicMock.__await__ = lambda x: async_magic().__await__()


def pull_mock(rv=None):
    if rv is None:
        rv = [object()]

    async def pull_coro(_):
        return rv

    return MagicMock(side_effect=pull_coro)


class DummyIterable():
    def __iter__(self):
        raise DummyException()


class TestLink(TestCase):

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_transfer(self, inlet, outlet):
        link = Link([inlet], [outlet], timedelta(
            seconds=1), tags='test_update')

        link.transfer()

        inlet._pull.assert_called()
        outlet._push.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_run(self, inlet, outlet):
        async def task():
            link = Link([inlet], [outlet], timedelta(seconds=1),
                        tags='test_run', copy_records=False)

            inlet_result = await inlet._pull(None)
            await link._run()

            inlet._pull.assert_called()
            outlet._push.assert_called_with(inlet_result, mock.ANY)

        asyncio.run(task())

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_exception_inlet(self, inlet, outlet):
        inlet._pull.side_effect = DummyException('Test exception')
        link = Link([inlet], [outlet], timedelta(seconds=1),
                    ignore_exceptions=False, tags='test_exception_inlet')

        self.assertRaises(DummyException, link.transfer)

        inlet._pull.assert_called()
        outlet._push.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_exception_outlet(self, inlet, outlet):
        # inlet._pull.return_value, _ = self.inlet_return()
        # inlet._pull.side_effect = pull_mock
        # inlet._pull.return_value = Future()
        outlet._push.side_effect = DummyException('Test exception')
        link = Link([inlet], [outlet], timedelta(seconds=1),
                    ignore_exceptions=False, tags='test_exception_outlet')
        link = Link([inlet], [outlet], timedelta(seconds=1),
                    ignore_exceptions=False, tags='test_exception_outlet')

        self.assertRaises(DummyException, link.transfer)

        inlet._pull.assert_called()
        outlet._push.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_exception_caught(self, inlet, outlet):
        inlet._pull.side_effect = DummyException('Test inlet exception')
        outlet._push.side_effect = DummyException('Test outlet exception')
        link = Link([inlet], [outlet], timedelta(seconds=1),
                    tags='test_exception_caught', ignore_exceptions=True)

        try:
            with self.assertLogs(logging.getLogger('databay.Link'), level='WARNING') as cm:
                link.transfer()
                self.assertTrue(
                    'Test inlet exception' in ';'.join(cm.output))
                self.assertTrue(
                    'Test outlet exception' in ';'.join(cm.output))
        except Exception as e:
            self.fail(f'Should not raise exception: {e}')

        inlet._pull.assert_called()
        outlet._push.assert_called()

    # check that one exception doesn't halt other inlets or outlets
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_ignore_partial_exception(self, inlet1, inlet2, outlet1, outlet2):

        async def task():
            # inlet_future = Future()
            inlet1._pull.side_effect = DummyException('Test inlet1 exception')
            outlet1._push.side_effect = DummyException(
                'Test outlet1 exception')
            # inlet1._pull.return_value = inlet_future
            # inlet2._pull.return_value = inlet_future
            link = Link([inlet1, inlet2], [outlet1, outlet2], timedelta(
                seconds=1), tags='test_ignore_partial_exception', copy_records=False, ignore_exceptions=True)

            # results = [object()]
            results = await inlet2._pull(None)
            # inlet_future.set_result(results)

            with self.assertLogs(logging.getLogger('databay.Link'), level='WARNING') as cm:
                await link._run()
                self.assertTrue(
                    'Test inlet1 exception' in ';'.join(cm.output))
                self.assertTrue(
                    'Test outlet1 exception' in ';'.join(cm.output))

            inlet1._pull.assert_called()
            inlet2._pull.assert_called()
            outlet1._push.assert_called_with(results, mock.ANY)
            outlet2._push.assert_called_with(results, mock.ANY)

        asyncio.run(task())

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_on_start(self, inlet1, outlet1):
        type(inlet1).active = mock.PropertyMock(return_value=False)
        type(outlet1).active = mock.PropertyMock(return_value=False)
        link = Link([inlet1], [outlet1], timedelta(
            seconds=1), tags='test_on_start')

        link.on_start()

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_on_start_already_active(self, inlet1, outlet1):
        type(inlet1).active = mock.PropertyMock(return_value=True)
        type(outlet1).active = mock.PropertyMock(return_value=True)
        link = Link([inlet1], [outlet1], timedelta(seconds=1),
                    tags='test_on_start_already_active')

        link.on_start()

        inlet1.on_start.assert_not_called()
        outlet1.on_start.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_on_shutdown(self, inlet1, outlet1):
        type(inlet1).active = mock.PropertyMock(return_value=True)
        type(outlet1).active = mock.PropertyMock(return_value=True)
        link = Link([inlet1], [outlet1], timedelta(
            seconds=1), tags='test_on_shutdown')

        link.on_shutdown()

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_already_inactive(self, inlet1, outlet1):
        type(inlet1).active = mock.PropertyMock(return_value=False)
        type(outlet1).active = mock.PropertyMock(return_value=False)
        link = Link([inlet1], [outlet1], timedelta(seconds=1),
                    tags='test_on_shutdown_already_inactive')

        link.on_shutdown()

        inlet1.on_shutdown.assert_not_called()
        outlet1.on_shutdown.assert_not_called()

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_add_inlet(self, inlet1):
        link = Link([], [], timedelta(seconds=1), tags='test_add_inlet')

        link.add_inlets(inlet1)

        self.assertEqual(link.inlets, [inlet1])


    def test_add_inlet_invalid(self):
        link = Link([], [], timedelta(seconds=1), tags='test_add_inlet')
        self.assertRaises(TypeError, link.add_inlets, "invalid_inlet")


    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_add_inlet_multiple(self, inlet1, inlet2):
        link = Link([], [], timedelta(seconds=1),
                    tags='test_add_inlet_multiple')

        link.add_inlets([inlet1, inlet2])

        self.assertEqual(link.inlets, [inlet1, inlet2])

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_add_inlet_same(self, inlet1):
        link = Link([], [], timedelta(seconds=1), tags='test_add_inlet_same')

        link.add_inlets(inlet1)
        self.assertRaises(InvalidNodeError, link.add_inlets, inlet1)

        self.assertEqual(link.inlets, [inlet1])

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_remove_inlet(self, inlet1, inlet2):
        link = Link([], [], timedelta(seconds=1), tags='test_remove_inlet')

        link.add_inlets([inlet1, inlet2])
        link.remove_inlets(inlet2)

        self.assertEqual(link.inlets, [inlet1])

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_remove_inlet_invalid(self, inlet1, inlet2):
        link = Link([], [], timedelta(seconds=1),
                    tags='test_remove_inlet_invalid')

        link.add_inlets([inlet1])

        self.assertRaises(InvalidNodeError, link.remove_inlets, inlet2)
        self.assertEqual(link.inlets, [inlet1])

    @patch(fqname(Outlet), spec=Outlet)
    def test_add_outlet(self, outlet1):
        link = Link([], [], timedelta(seconds=1), tags='test_add_outlet')

        link.add_outlets(outlet1)

        self.assertEqual(link.outlets, [outlet1])

    def test_add_outlet_invalid(self):
        link = Link([], [], timedelta(seconds=1), tags='test_add_outlet')
        self.assertRaises(TypeError, link.add_outlets, "invalid_outlet")

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    def test_add_outlet_multiple(self, outlet1, outlet2):
        link = Link([], [], timedelta(seconds=1),
                    tags='test_add_outlet_multiple')

        link.add_outlets([outlet1, outlet2])

        self.assertEqual(link.outlets, [outlet1, outlet2])

    @patch(fqname(Outlet), spec=Outlet)
    def test_add_outlet_same(self, outlet1):
        link = Link([], [], timedelta(seconds=1), tags='test_add_outlet_same')

        link.add_outlets(outlet1)
        self.assertRaises(InvalidNodeError, link.add_outlets, outlet1)

        self.assertEqual(link.outlets, [outlet1])

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    def test_remove_outlet(self, outlet1, outlet2):
        link = Link([], [], timedelta(seconds=1), tags='test_remove_outlet')

        link.add_outlets([outlet1, outlet2])
        link.remove_outlets(outlet2)

        self.assertEqual(link.outlets, [outlet1])

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    def test_remove_outlet_invalid(self, outlet1, outlet2):
        link = Link([], [], timedelta(seconds=1),
                    tags='test_remove_outlet_invalid')

        link.add_outlets([outlet1])

        self.assertRaises(InvalidNodeError, link.remove_outlets, outlet2)
        self.assertEqual(link.outlets, [outlet1])

    # this rv is invalid, should be a list
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock(object()))
    def xtest_non_iterable_raised(self, inlet1):
        logging.getLogger('databay.Link').setLevel(logging.ERROR)
        link = Link([inlet1], [], timedelta(seconds=1),
                    tags='test_non_iterable_raised')
        with self.assertRaisesRegex(TypeError, 'Inlets must return iterable'):
            link.transfer()

    # this rv will raise DummyException
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock(DummyIterable()))
    def test_generic_error_raised(self, inlet1):
        link = Link([inlet1], [], timedelta(seconds=1),
                    tags='test_generic_error_raised')
        # with self.assertRaisesRegex(TypeError, databay.link._ITERABLE_EXCEPTION):
        self.assertRaises(DummyException, link.transfer)

    def test_integer_to_timedelta(self):
        link = Link([], [], 1, name='test_integer_interval_coerced')
        self.assertEqual(link._interval, timedelta(seconds=1))

    def test_float_to_timedelta(self):
        link = Link([], [], 1.5, name='test_float_interval_coerced')
        self.assertEqual(link._interval, timedelta(seconds=1.5))

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_start_inlet_exception_raise(self, inlet1, outlet1):
        inlet1.try_start.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1], timedelta(
            seconds=1), tags='test_on_start')

        self.assertRaises(RuntimeError, link.on_start)

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_start_inlet_exception_catch(self, inlet1, outlet1):
        inlet1.try_start.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1], timedelta(seconds=1),
                    tags='test_on_start', ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.on_start()
            self.assertTrue(
                'on_start inlet exception: "" for inlet:' in ';'.join(cm.output))

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_start_outlet_exception_raise(self, inlet1, outlet1, outlet2):
        outlet1.try_start.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1, outlet2],
                    timedelta(seconds=1), tags='test_on_start')

        self.assertRaises(RuntimeError, link.on_start)

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_called()
        outlet2.try_start.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_start_outlet_exception_catch(self, inlet1, outlet1, outlet2):
        outlet1.try_start.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1, outlet2], timedelta(
            seconds=1), tags='test_on_start', ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.on_start()
            self.assertTrue(
                'on_start outlet exception: "" for outlet:' in ';'.join(cm.output), cm.output)

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_called()
        outlet2.try_start.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_inlet_exception_raise(self, inlet1, outlet1):
        inlet1.try_shutdown.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1], timedelta(
            seconds=1), tags='test_on_shutdown')

        self.assertRaises(RuntimeError, link.on_shutdown)

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_inlet_exception_catch(self, inlet1, outlet1):
        inlet1.try_shutdown.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1], timedelta(seconds=1),
                    tags='test_on_shutdown', ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.on_shutdown()
            self.assertTrue(
                'on_shutdown inlet exception: "" for inlet:' in ';'.join(cm.output), cm.output)

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_outlet_exception_raise(self, inlet1, outlet1, outlet2):
        outlet1.try_shutdown.side_effect = lambda: exec(
            'raise(RuntimeError())')
        link = Link([inlet1], [outlet1, outlet2], timedelta(
            seconds=1), tags='test_on_shutdown')

        self.assertRaises(RuntimeError, link.on_shutdown)

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_called()
        outlet2.try_shutdown.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_outlet_exception_catch(self, inlet1, outlet1, outlet2):
        outlet1.try_shutdown.side_effect = lambda: exec(
            'raise(RuntimeError())')
        link = Link([inlet1], [outlet1, outlet2], timedelta(
            seconds=1), tags='test_on_shutdown', ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.on_shutdown()
            self.assertTrue('on_shutdown outlet exception: "" for outlet:' in ';'.join(
                cm.output), cm.output)

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_called()
        outlet2.try_shutdown.assert_called()

    def test_single_tag(self):
        tag = 'tagA'
        link = Link([], [], timedelta(seconds=1), tags=tag)
        self.assertEqual(link.tags, [tag])

    def test_multiple_tags(self):
        tagA = 'tagA'
        tagB = 'tagB'
        link = Link([], [], timedelta(seconds=1), tags=[tagA, tagB])
        self.assertEqual(link.tags, [tagA, tagB])

    def test_tag_as_name(self):
        link_name = 'link_name'
        link = Link([], [], timedelta(seconds=1), name=link_name)
        self.assertEqual(link_name, link.tags[0])

    def test_name_from_tag(self):
        link_name = 'link_name'
        link = Link([], [], timedelta(seconds=1), tags=[link_name])
        self.assertEqual(link.name, link.tags[0])

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    @patch(fqname(Inlet), spec=Inlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_inlet_concurrency(self, inlet1, inlet2, inlet3, outlet):
        counter = {'value': 0}

        # this will increment the counter on each async call, and check if they exceed the concurrency value
        async def slow_pull(_):
            counter['value'] += 1
            self.assertLessEqual(counter['value'], 2, "Only 2 inlets should pull at a time")
            await asyncio.sleep(0.01)
            counter['value'] -= 1
            return [123]

        inlet1._pull = slow_pull
        inlet2._pull = slow_pull
        inlet3._pull = slow_pull

        async def task():
            link = Link([inlet1, inlet2, inlet3], [outlet],
                        timedelta(seconds=1),
                        tags='test_inlet_concurrency',
                        copy_records=False,
                        inlet_concurrency=2)

            await link._run()

        asyncio.run(task())

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_processors_one(self, inlet, outlet):
        records = [2, 3]
        inlet._pull = pull_mock(records)
        processor = MagicMock(side_effect = lambda r: r)
        link = Link(inlet, outlet, interval=0.01, processors=processor)
        link.transfer()
        processor.assert_called_with(records)
        outlet._push.assert_called_with(records, mock.ANY)

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_processors_many(self, inlet, outlet):
        records = [2, 3]
        inlet._pull = pull_mock(records)
        processorA = MagicMock(side_effect = lambda x: x)
        processorB = MagicMock(side_effect = lambda x: x)
        link = Link(inlet, outlet, interval=0.01, processors=[processorA, processorB])
        link.transfer()
        processorA.assert_called_with(records)
        processorB.assert_called_with(records)
        outlet._push.assert_called_with(records, mock.ANY)

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_processors_change_records(self, inlet, outlet):
        records = [2, 3]
        inlet._pull = pull_mock(records)
        processorA = MagicMock(side_effect = lambda r: list(map(lambda y: y*y, r)))
        processorB = MagicMock(side_effect = lambda r: list(map(lambda y: -y, r)))
        link = Link(inlet, outlet, interval=0.01, processors=[processorA, processorB])
        link.transfer()
        processorA.assert_called_with(records)
        processorB.assert_called_with([4, 9])
        outlet._push.assert_called_with([-4, -9], mock.ANY)

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_processors_filter_records(self, inlet, outlet):
        records = [2, 3, 4]
        inlet._pull = pull_mock(records)
        processorA = MagicMock(side_effect = lambda r: list(filter(lambda y: y>2, r)))
        processorB = MagicMock(side_effect = lambda r: list(filter(lambda y: y%2==0, r)))
        link = Link(inlet, outlet, interval=0.01, processors=[processorA, processorB])
        link.transfer()
        processorA.assert_called_with(records)
        processorB.assert_called_with([3, 4])
        outlet._push.assert_called_with([4], mock.ANY)

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_batchers_one_passive(self, inlet, outlet):
        records = [1, 2, 3, 4]
        inlet._pull = pull_mock(records)
        batcher = MagicMock(side_effect=lambda r: r) # does nothing on purpose
        link = Link(inlet, outlet, interval=0.01, batchers=batcher)
        link.transfer()
        batcher.assert_called_with([records])
        outlet._push.assert_called_with(records, mock.ANY)

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_batchers_one_active(self, inlet, outlet):
        records = [1, 2, 3, 4]
        inlet._pull = pull_mock(records)

        # makes [[1,2], [3,4]]
        batcher = MagicMock(side_effect=lambda r: [r[0][:2], r[0][2:]])

        link = Link(inlet, outlet, interval=0.01, batchers=batcher)
        link.transfer()
        batcher.assert_called_with([records])
        calls = [call(records[:2], mock.ANY), call(records[2:], mock.ANY)]
        outlet._push.assert_has_calls(calls) # expects [[1,2], [3,4]]

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_batchers_many_active(self, inlet, outlet):
        records = [1, 2, 3, 4]
        inlet._pull = pull_mock(records)

        # makes [[1,2], [3,4]]
        batcherA = MagicMock(side_effect=lambda r: [r[0][:2], r[0][2:]])

        # makes [[1], [2], [3], [4]]
        batcherB = MagicMock(side_effect=lambda r: [[sub] for sub in r[0]] + [[sub] for sub in r[1]])

        link = Link(inlet, outlet, interval=0.01, batchers=[batcherA, batcherB])
        link.transfer()

        batcherA.assert_called_with([records])

        callsA = [call([records[:2], records[2:]])] # expects [[1,2], [3,4]]
        batcherB.assert_has_calls(callsA)

        callsB = [call([records[0]], mock.ANY),
                  call([records[1]], mock.ANY),
                  call([records[2]], mock.ANY),
                  call([records[3]], mock.ANY)]
        outlet._push.assert_has_calls(callsB) # expects [[1], [2], [3], [4]]

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_processor_exception(self, inlet, outlet):
        records = [2, 3]
        inlet._pull = pull_mock(records)
        processor = MagicMock(side_effect = DummyException('Processor exception'))
        link = Link(inlet, outlet, interval=0.01, processors=processor)
        self.assertRaises(DummyException, link.transfer)
        processor.assert_called_with(records)
        outlet._push.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_processor_exception_ignored(self, inlet, outlet):
        records = [2, 3]
        inlet._pull = pull_mock(records)
        processorA = MagicMock(side_effect = DummyException('Processor exception'))
        processorB = MagicMock(side_effect = lambda r: list(map(lambda y: y*y, r)))
        link = Link(inlet, outlet, interval=0.01, processors=[processorA, processorB], ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.transfer()
            self.assertTrue('Processor exception:' in ';'.join(
                cm.output), cm.output)

        processorA.assert_called_with(records)
        processorB.assert_called_with(records)
        outlet._push.assert_called_with([4,9], mock.ANY)

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_batcher_exception(self, inlet, outlet):
        records = [2, 3]
        inlet._pull = pull_mock(records)
        batcher = MagicMock(side_effect = DummyException('Batcher exception'))
        link = Link(inlet, outlet, interval=0.01, batchers=batcher)
        self.assertRaises(DummyException, link.transfer)
        batcher.assert_called_with([records])
        outlet._push.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_batcher_exception_ignored(self, inlet, outlet):
        records = [1, 2, 3, 4]
        inlet._pull = pull_mock(records)
        batcherA = MagicMock(side_effect = DummyException('Batcher exception'))
        batcherB = MagicMock(side_effect=lambda r: [r[0][:2], r[0][2:]])
        link = Link(inlet, outlet, interval=0.01, batchers=[batcherA, batcherB], ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.transfer()
            self.assertTrue('Batcher exception:' in ';'.join(
                cm.output), cm.output)

        batcherA.assert_called_with([records])
        batcherB.assert_called_with([records])
        calls = [call(records[:2], mock.ANY), call(records[2:], mock.ANY)]
        outlet._push.assert_has_calls(calls)  # expects [[1,2], [3,4]]

