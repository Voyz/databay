import logging
import time
from unittest import TestCase
from unittest.mock import MagicMock

from databay import Record
from databay.support.buffers import Buffer
from test_utils import DummyException


class TestBuffers(TestCase):

    def test_count_controller(self):
        buffer = Buffer(count_threshold=10)
        payload = [1,2,3,4,5,6,7,8,9,10,11]
        records = [Record(payload=p) for p in payload]
        result_false = buffer._count_controller(records[:6])
        result_true = buffer._count_controller(records)
        self.assertFalse(result_false, 'Count controller should return False with 6 records')
        self.assertTrue(result_true, 'Count controller should return True with 11 records')

    def test_time_controller(self):
        buffer = Buffer(time_threshold=0.01)
        payload = [1,2,3]
        records = [Record(payload=p) for p in payload]
        result_false = buffer._time_controller(records)
        time.sleep(0.01)
        result_true = buffer._time_controller(records)
        self.assertFalse(result_false, 'Time controller should return False after less than 0.01 seconds')
        self.assertTrue(result_true, 'Time controller should return True after sleeping for 0.01 seconds')

    def test_get_controllers(self):
        custom_controller = lambda x: True

        buffer = Buffer()
        self.assertEqual(buffer.get_controllers(), [], 'Should not have any controllers')

        buffer = Buffer(time_threshold=1)
        self.assertEqual(buffer.get_controllers(), [buffer._time_controller], 'Should have only time controller')

        buffer = Buffer(count_threshold=1)
        self.assertEqual(buffer.get_controllers(), [buffer._count_controller], 'Should have only count controller')

        buffer = Buffer(custom_controllers = [custom_controller])
        self.assertEqual(buffer.get_controllers(), [custom_controller], 'Should have only custom controller')

        buffer = Buffer(time_threshold=1, count_threshold=1, custom_controllers = [custom_controller])
        self.assertEqual(buffer.get_controllers(), [custom_controller, buffer._count_controller, buffer._time_controller], 'Should have all controllers')

    def test_reset(self):
        buffer = Buffer()
        buffer.records = [1,2,3]
        buffer.time_start = time.time()
        buffer.reset()
        self.assertEqual(buffer.records, [], 'Buffer.records should be reset to []')
        self.assertIsNone(buffer.time_start, 'Buffer.time_start should be reset to None')

    def test_execute_disjoint(self):
        custom_controller = MagicMock(side_effect= lambda x: False)
        buffer = Buffer(count_threshold=1, time_threshold=1, custom_controllers=custom_controller)
        buffer._count_controller = MagicMock(side_effect= lambda x: False)
        buffer._time_controller = MagicMock(side_effect= lambda x: False)
        payload = [1,2,3]
        records = [Record(payload=p) for p in payload]
        buffer._execute(records)
        buffer._count_controller.assert_called_with(records)
        buffer._time_controller.assert_called_with(records)
        custom_controller.assert_called_with(records)

    def test_execute_conjoint_false(self):
        custom_controller = MagicMock(side_effect= lambda x: True)
        buffer = Buffer(count_threshold=1, time_threshold=1, custom_controllers=custom_controller, conjugate_controllers=True)
        buffer._count_controller = MagicMock(side_effect= lambda x: False)
        buffer._time_controller = MagicMock(side_effect= lambda x: True)
        payload = [1,2,3]
        records = [Record(payload=p) for p in payload]
        buffer._execute(records)
        custom_controller.assert_called_with(records)
        buffer._count_controller.assert_called_with(records)
        buffer._time_controller.assert_not_called()

    def test_execute_conjoint_true(self):
        custom_controller = MagicMock(side_effect= lambda x: True)
        buffer = Buffer(count_threshold=1, time_threshold=1, custom_controllers=custom_controller, conjugate_controllers=True)
        buffer._count_controller = MagicMock(side_effect= lambda x: True)
        buffer._time_controller = MagicMock(side_effect= lambda x: True)
        payload = [1,2,3]
        records = [Record(payload=p) for p in payload]
        result = buffer._execute(records)
        buffer._count_controller.assert_called_with(records)
        buffer._time_controller.assert_called_with(records)
        custom_controller.assert_called_with(records)
        self.assertEqual(result, records)



    def test_execute_count(self):
        buffer = Buffer(count_threshold=10)
        payload = [1,2,3,4,5,6,7,8,9,10,11]
        records = [Record(payload=p) for p in payload]
        rvA = buffer(records[:6])
        rvB = buffer(records[6:])
        self.assertEqual(rvA, [], 'Should not contain any records yet')
        self.assertEqual(rvB, records, 'Should contain all records')

    def test_execute_time(self):
        buffer = Buffer(time_threshold=0.01)
        payload = [1,2,3,4,5,6,7,8,9,10,11]
        records = [Record(payload=p) for p in payload]
        rvA = buffer(records[:6])
        time.sleep(0.01)
        rvB = buffer(records[6:])
        self.assertEqual(rvA, [], 'Should not contain any records yet')
        self.assertEqual(rvB, records, 'Should contain all records')

    def test_execute_custom(self):
        # checks if number 11 is in the any of the records' payload
        custom_controller = lambda x: len(list(filter(lambda v: v.payload==11, x)))

        buffer = Buffer(custom_controllers=custom_controller)
        payload = [1,2,3,4,5,6,7,8,9,10,11]
        records = [Record(payload=p) for p in payload]
        rvA = buffer(records[:6])
        rvB = buffer(records[6:])
        self.assertEqual(rvA, [], 'Should not contain any records yet')
        self.assertEqual(rvB, records, 'Should contain all records')

    def test_execute_time_before_count(self):
        buffer = Buffer(count_threshold=10, time_threshold=0.04)
        payload = [1,2,3,4,5,6,7,8,9,10,11]
        records = [Record(payload=p) for p in payload]
        rv = []
        for r in records:
            # print(r, buffer.records)
            rv = buffer([r])
            if rv != []:
                break
            time.sleep(0.02)

        self.assertEqual(rv, records[:3], 'Should contain 3 records')
        self.assertEqual(buffer.records, [], 'Buffer.records should be reset to []')
        self.assertIsNone(buffer.time_start, 'Buffer.time_start should be reset to None')

    def test_execute_count_before_time(self):
        buffer = Buffer(count_threshold=10, time_threshold=1)
        payload = [1,2,3,4,5,6,7,8,9,10,11]
        records = [Record(payload=p) for p in payload]
        rv = []
        for r in records:
            rv = buffer([r])
            if rv != []:
                break

        self.assertEqual(rv, records, 'Should contain all records')
        self.assertEqual(buffer.records, [], 'Buffer.records should be reset to []')
        self.assertIsNone(buffer.time_start, 'Buffer.time_start should be reset to None')

    def test_flush(self):
        buffer = Buffer(count_threshold=100, time_threshold=10)
        payload = [1,2,3,4,5,6,7,8,9,10,11]
        records = [Record(payload=p) for p in payload]
        buffer.flush = False
        rvA = buffer(records[:6])
        buffer.flush = True
        rvB = buffer(records[6:])
        self.assertEqual(rvA, [], 'Should not contain any records yet')
        self.assertEqual(rvB, records, 'Should contain all records')


    def test_on_reset(self):
        custom_controller = MagicMock()
        on_reset = MagicMock()
        buffer = Buffer(custom_controllers=custom_controller, on_reset=on_reset)
        payload = [1,2]
        records = [Record(payload=p) for p in payload]
        buffer(records)
        custom_controller.assert_called_with(records)
        self.assertEqual(on_reset.call_count, 1)
        buffer.reset()
        self.assertEqual(on_reset.call_count, 2)

    def test_custom_exception(self):
        custom_controller = MagicMock(side_effect=DummyException('Custom controller exception!'))
        payload = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

        records = [Record(payload=p) for p in payload]
        buffer = Buffer(count_threshold=10, custom_controllers=custom_controller)

        with self.assertLogs(logging.getLogger('databay.Buffer'), level='DEBUG') as cm:
            rvA = buffer(records[:6])
            rvB = buffer(records[6:])
            self.assertTrue(
                'Custom controller exception!' in ';'.join(cm.output))

        self.assertEqual(rvA, [], 'Should not contain any records yet')
        self.assertEqual(rvB, records, 'Should contain all records')

    def test_custom_exception_conjoint(self):
        custom_controller = MagicMock(side_effect=DummyException('Custom controller exception!'))
        payload = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

        records = [Record(payload=p) for p in payload]
        buffer = Buffer(count_threshold=10, custom_controllers=custom_controller, conjugate_controllers=True)

        with self.assertLogs(logging.getLogger('databay.Buffer'), level='DEBUG') as cm:
            rvA = buffer(records[:6])
            rvB = buffer(records[6:])
            self.assertTrue(
                'Custom controller exception!' in ';'.join(cm.output))

        self.assertEqual(rvA, [], 'Should not contain any records yet')
        self.assertEqual(rvB, records, 'Should contain all records')

