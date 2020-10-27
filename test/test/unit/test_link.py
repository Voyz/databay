import asyncio
import logging
from asyncio import Future
from datetime import timedelta
from unittest import TestCase, mock
from unittest.mock import MagicMock, patch

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

    return mock.MagicMock(side_effect=pull_coro)


class DummyIterable():
    def __iter__(self):
        raise DummyException()


class TestLink(TestCase):

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_transfer(self, inlet, outlet):
        link = Link([inlet], [outlet], timedelta(
            seconds=1), name='test_update')

        link.transfer()

        inlet._pull.assert_called()
        outlet._push.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_run(self, inlet, outlet):
        async def task():
            link = Link([inlet], [outlet], timedelta(seconds=1),
                        name='test_run', copy_records=False)

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
                    ignore_exceptions=False, name='test_exception_inlet')

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
                    ignore_exceptions=False, name='test_exception_outlet')

        self.assertRaises(DummyException, link.transfer)

        inlet._pull.assert_called()
        outlet._push.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_exception_caught(self, inlet, outlet):
        logging.getLogger('databay.Link').setLevel(logging.CRITICAL)
        inlet._pull.side_effect = DummyException('Test inlet exception')
        outlet._push.side_effect = DummyException('Test outlet exception')
        link = Link([inlet], [outlet], timedelta(seconds=1),
                    name='test_exception_caught', ignore_exceptions=True)

        try:
            link.transfer()
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
        logging.getLogger('databay.Link').setLevel(logging.CRITICAL)

        async def task():
            # inlet_future = Future()
            inlet1._pull.side_effect = DummyException('Test inlet1 exception')
            outlet1._push.side_effect = DummyException(
                'Test outlet1 exception')
            # inlet1._pull.return_value = inlet_future
            # inlet2._pull.return_value = inlet_future
            link = Link([inlet1, inlet2], [outlet1, outlet2], timedelta(
                seconds=1), name='test_ignore_partial_exception', copy_records=False, ignore_exceptions=True)

            # results = [object()]
            results = await inlet2._pull(None)
            # inlet_future.set_result(results)

            await link._run()

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
            seconds=1), name='test_on_start')

        link.on_start()

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_on_start_already_active(self, inlet1, outlet1):
        type(inlet1).active = mock.PropertyMock(return_value=True)
        type(outlet1).active = mock.PropertyMock(return_value=True)
        link = Link([inlet1], [outlet1], timedelta(seconds=1),
                    name='test_on_start_already_active')

        link.on_start()

        inlet1.on_start.assert_not_called()
        outlet1.on_start.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_on_shutdown(self, inlet1, outlet1):
        type(inlet1).active = mock.PropertyMock(return_value=True)
        type(outlet1).active = mock.PropertyMock(return_value=True)
        link = Link([inlet1], [outlet1], timedelta(
            seconds=1), name='test_on_shutdown')

        link.on_shutdown()

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_already_inactive(self, inlet1, outlet1):
        type(inlet1).active = mock.PropertyMock(return_value=False)
        type(outlet1).active = mock.PropertyMock(return_value=False)
        link = Link([inlet1], [outlet1], timedelta(seconds=1),
                    name='test_on_shutdown_already_inactive')

        link.on_shutdown()

        inlet1.on_shutdown.assert_not_called()
        outlet1.on_shutdown.assert_not_called()

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_add_inlet(self, inlet1):
        link = Link([], [], timedelta(seconds=1), name='test_add_inlet')

        link.add_inlets(inlet1)

        self.assertEqual(link.inlets, [inlet1])

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_add_inlet_multiple(self, inlet1, inlet2):
        link = Link([], [], timedelta(seconds=1),
                    name='test_add_inlet_multiple')

        link.add_inlets([inlet1, inlet2])

        self.assertEqual(link.inlets, [inlet1, inlet2])

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_add_inlet_same(self, inlet1):
        link = Link([], [], timedelta(seconds=1), name='test_add_inlet_same')

        link.add_inlets(inlet1)
        self.assertRaises(InvalidNodeError, link.add_inlets, inlet1)

        self.assertEqual(link.inlets, [inlet1])

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_remove_inlet(self, inlet1, inlet2):
        link = Link([], [], timedelta(seconds=1), name='test_remove_inlet')

        link.add_inlets([inlet1, inlet2])
        link.remove_inlets(inlet2)

        self.assertEqual(link.inlets, [inlet1])

    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock())
    def test_remove_inlet_invalid(self, inlet1, inlet2):
        link = Link([], [], timedelta(seconds=1),
                    name='test_remove_inlet_invalid')

        link.add_inlets([inlet1])

        self.assertRaises(InvalidNodeError, link.remove_inlets, inlet2)
        self.assertEqual(link.inlets, [inlet1])

    @patch(fqname(Outlet), spec=Outlet)
    def test_add_outlet(self, outlet1):
        link = Link([], [], timedelta(seconds=1), name='test_add_outlet')

        link.add_outlets(outlet1)

        self.assertEqual(link.outlets, [outlet1])

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    def test_add_outlet_multiple(self, outlet1, outlet2):
        link = Link([], [], timedelta(seconds=1),
                    name='test_add_outlet_multiple')

        link.add_outlets([outlet1, outlet2])

        self.assertEqual(link.outlets, [outlet1, outlet2])

    @patch(fqname(Outlet), spec=Outlet)
    def test_add_outlet_same(self, outlet1):
        link = Link([], [], timedelta(seconds=1), name='test_add_outlet_same')

        link.add_outlets(outlet1)
        self.assertRaises(InvalidNodeError, link.add_outlets, outlet1)

        self.assertEqual(link.outlets, [outlet1])

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    def test_remove_outlet(self, outlet1, outlet2):
        link = Link([], [], timedelta(seconds=1), name='test_remove_outlet')

        link.add_outlets([outlet1, outlet2])
        link.remove_outlets(outlet2)

        self.assertEqual(link.outlets, [outlet1])

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    def test_remove_outlet_invalid(self, outlet1, outlet2):
        link = Link([], [], timedelta(seconds=1),
                    name='test_remove_outlet_invalid')

        link.add_outlets([outlet1])

        self.assertRaises(InvalidNodeError, link.remove_outlets, outlet2)
        self.assertEqual(link.outlets, [outlet1])

    # this rv is invalid, should be a list
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock(object()))
    def xtest_non_iterable_raised(self, inlet1):
        logging.getLogger('databay.Link').setLevel(logging.ERROR)
        link = Link([inlet1], [], timedelta(seconds=1),
                    name='test_non_iterable_raised')
        with self.assertRaisesRegex(TypeError, 'Inlets must return iterable'):
            link.transfer()

    # this rv will raise DummyException
    @patch(fqname(Inlet), spec=Inlet, _pull=pull_mock(DummyIterable()))
    def test_generic_error_raised(self, inlet1):
        logging.getLogger('databay.Link').setLevel(logging.ERROR)
        link = Link([inlet1], [], timedelta(seconds=1),
                    name='test_generic_error_raised')
        # with self.assertRaisesRegex(TypeError, databay.link._ITERABLE_EXCEPTION):
        self.assertRaises(DummyException, link.transfer)

    def test_integer_to_timedelta(self):
        link = Link([], [], 1, name='test_integer_interval_coerced')
        self.assertEquals(link._interval, timedelta(seconds=1))

    def test_float_to_timedelta(self):
        link = Link([], [], 1.5, name='test_float_interval_coerced')
        self.assertEquals(link._interval, timedelta(seconds=1.5))

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_start_inlet_exception_raise(self, inlet1, outlet1):
        inlet1.try_start.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1], timedelta(seconds=1), name='test_on_start')

        self.assertRaises(RuntimeError, link.on_start)

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_start_inlet_exception_catch(self, inlet1, outlet1):
        logging.getLogger('databay.Link').setLevel(logging.WARNING)
        inlet1.try_start.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1], timedelta(seconds=1), name='test_on_start', ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.on_start()
        self.assertTrue('on_start inlet exception: "" for inlet:' in ';'.join(cm.output))

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_start_outlet_exception_raise(self, inlet1, outlet1, outlet2):
        outlet1.try_start.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1, outlet2], timedelta(seconds=1), name='test_on_start')

        self.assertRaises(RuntimeError, link.on_start)

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_called()
        outlet2.try_start.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_start_outlet_exception_catch(self, inlet1, outlet1, outlet2):
        logging.getLogger('databay.Link').setLevel(logging.WARNING)
        outlet1.try_start.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1, outlet2], timedelta(seconds=1), name='test_on_start', ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.on_start()
        self.assertTrue('on_start outlet exception: "" for outlet:' in ';'.join(cm.output), cm.output)

        inlet1.try_start.assert_called()
        outlet1.try_start.assert_called()
        outlet2.try_start.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_inlet_exception_raise(self, inlet1, outlet1):
        inlet1.try_shutdown.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1], timedelta(seconds=1), name='test_on_shutdown')

        self.assertRaises(RuntimeError, link.on_shutdown)

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_inlet_exception_catch(self, inlet1, outlet1):
        logging.getLogger('databay.Link').setLevel(logging.WARNING)
        inlet1.try_shutdown.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1], timedelta(seconds=1), name='test_on_shutdown', ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.on_shutdown()
        self.assertTrue('on_shutdown inlet exception: "" for inlet:' in ';'.join(cm.output), cm.output)

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_outlet_exception_raise(self, inlet1, outlet1, outlet2):
        outlet1.try_shutdown.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1, outlet2], timedelta(seconds=1), name='test_on_shutdown')

        self.assertRaises(RuntimeError, link.on_shutdown)

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_called()
        outlet2.try_shutdown.assert_not_called()

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_on_shutdown_outlet_exception_catch(self, inlet1, outlet1, outlet2):
        logging.getLogger('databay.Link').setLevel(logging.WARNING)
        outlet1.try_shutdown.side_effect = lambda: exec('raise(RuntimeError())')
        link = Link([inlet1], [outlet1, outlet2], timedelta(seconds=1), name='test_on_shutdown', ignore_exceptions=True)

        with self.assertLogs(logging.getLogger('databay.Link'), level='ERROR') as cm:
            link.on_shutdown()
        self.assertTrue('on_shutdown outlet exception: "" for outlet:' in ';'.join(cm.output), cm.output)

        inlet1.try_shutdown.assert_called()
        outlet1.try_shutdown.assert_called()
        outlet2.try_shutdown.assert_called()
