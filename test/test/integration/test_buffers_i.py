import time
from threading import Thread
from unittest import TestCase, mock
from unittest.mock import MagicMock, patch

from databay import Record, Inlet, Outlet, Link
from databay.misc.buffers import Buffer
from databay.planners import SchedulePlanner
from test_utils import fqname
from unit.test_link import pull_mock


class TestBuffers(TestCase):

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_buffer_count(self, inlet, outlet):
        buffer = Buffer(count_threshold=3)

        payload = [1,2,3,4]
        records = [Record(payload=p) for p in payload]

        link = Link(inlet, outlet, interval=1, processors=buffer, copy_records=False)

        inlet._pull = pull_mock(records[:2])
        link.transfer()
        outlet._push.assert_called_with([], mock.ANY) # after first call we shouldn't have any records

        inlet._pull = pull_mock(records[2:])
        link.transfer()
        outlet._push.assert_called_with(records, mock.ANY) # all records should be returned here

    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_buffer_time(self, inlet, outlet):
        buffer = Buffer(time_threshold=0.02)

        payload = [1,2,3,4]
        records = [Record(payload=p) for p in payload]

        link = Link(inlet, outlet, interval=1, processors=buffer, copy_records=False)

        inlet._pull = pull_mock(records[:2])
        link.transfer()
        outlet._push.assert_called_with([], mock.ANY) # not enough time have passed

        inlet._pull = pull_mock(records[2:])
        link.transfer()
        outlet._push.assert_called_with([], mock.ANY) # not enough time have passed

        time.sleep(0.02)

        inlet._pull = pull_mock([])
        link.transfer()
        outlet._push.assert_called_with(records, mock.ANY) # all records should be returned here



    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_flush(self, inlet, outlet):
        buffer = Buffer(count_threshold=100, time_threshold=10)

        payload = [1,2,3,4]
        records = [Record(payload=p) for p in payload]

        link = Link(inlet, outlet, interval=1, processors=buffer, copy_records=False)

        inlet._pull = pull_mock(records[:2])
        link.transfer()
        outlet._push.assert_called_with([], mock.ANY) # no records yet

        inlet._pull = pull_mock(records[2:])
        link.transfer()
        outlet._push.assert_called_with([], mock.ANY) # no records yet

        buffer.flush = True
        inlet._pull = pull_mock([])
        link.transfer()
        outlet._push.assert_called_with(records, mock.ANY)  # all records should be flushed


    @patch(fqname(Outlet), spec=Outlet)
    @patch(fqname(Inlet), spec=Inlet)
    def test_flush_after_shutdown(self, inlet, outlet):
        buffer = Buffer(count_threshold=100, time_threshold=10)

        counter_dict = {'counter': 0, 'records': []}

        link = Link(inlet, outlet, interval=0.01, processors=buffer, copy_records=False)
        planner = SchedulePlanner(link, refresh_interval=0.01)

        async def pull_coro(_):
            # counter += 1
            counter_dict['counter'] += 1
            record = Record(payload=counter_dict['counter'])
            counter_dict['records'].append(record)
            return [record]

        mock_pull = MagicMock(side_effect=pull_coro)
        inlet._pull = mock_pull

        th = Thread(target=planner.start, daemon=True)
        th.start()
        time.sleep(0.1)

        planner.shutdown()
        th.join()

        calls = outlet._push.call_args_list
        for c in calls:
            self.assertEqual(c(), [], 'Should only contain empty record lists.' )
        self.assertEqual(buffer.records, counter_dict['records'], 'All records should be stored in the buffer')

        planner.force_transfer()
        self.assertEqual(outlet._push.call_args(), [], 'Should return empty record list')

        buffer.flush = True
        planner.force_transfer()
        self.assertEqual(outlet._push.call_args[0][0], counter_dict['records'], 'Should return all records')

