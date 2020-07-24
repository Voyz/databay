import logging
import time
from datetime import timedelta
from threading import Thread
from unittest import TestCase, mock
from unittest.mock import Mock, patch

import schedule

import databay
from databay import Link
from databay.errors import MissingLinkError
from databay.planners import SchedulePlanner
from databay.planners.schedule_planner import ScheduleIntervalError
from stubs.LinkStub import LinkStub
from test_utils import fqname, DummyException


class TestSchedulePlanner(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.getLogger('databay').setLevel(logging.WARNING)

    def setUp(self):
        self.planner = SchedulePlanner(refresh_interval=0.02)

    def tearDown(self):
        if len(schedule.jobs) > 0:
            schedule.clear()

    def test__run_job(self):
        link = mock.MagicMock()
        link.transfer = mock.MagicMock()
        self.planner._create_thread_pool()
        self.planner._run_job(link)
        link.transfer.assert_called_once()
        self.planner._destroy_thread_pool()

    def test__schedule(self):
        link = LinkStub([], [], timedelta(seconds=1))
        self.planner._schedule(link)
        self.assertIsNotNone(link.job, 'Link should contain a job')
        schedule_job = schedule.jobs[0]
        self.assertEqual(link.job, schedule_job, 'Link\'s job should be same as schedule\'s')
        # self.planner._unschedule(link)

    def test__unschedule(self):
        link = LinkStub([], [], timedelta(seconds=1))
        self.planner._schedule(link)
        self.planner._unschedule(link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertEqual(len(schedule.jobs), 0, 'Schedule should not have any jobs')

    def test__unschedule_invalid(self):
        link = LinkStub([], [], timedelta(seconds=1))
        self.planner._unschedule(link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertEqual(len(schedule.jobs), 0, 'Scheduler should not have any jobs')

    def test_add_link(self):
        link = LinkStub([], [], timedelta(seconds=1))
        self.planner.add_link(link)
        self.assertIsNotNone(link.job, 'Link should contain a job')
        self.assertTrue(link in self.planner.links, 'Planner should contain the link')

    def test_remove_link(self):
        link = LinkStub([], [], timedelta(seconds=1))
        self.planner.add_link(link)
        self.planner.remove_link(link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertTrue(link not in self.planner.links, 'Planner should not contain the link')

    def test_remove_invalid_link(self):
        link = LinkStub([], [], timedelta(seconds=1))
        self.assertRaises(MissingLinkError, self.planner.remove_link, link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertTrue(link not in self.planner.links, 'Planner should not contain the link')

    def test_start(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.assertTrue(self.planner._running, 'Planner should be running')
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown()
        self.assertFalse(self.planner._running, 'Planner should be not running')
        self.assertIsNone(self.planner._thread_pool, 'Planner should not have a thread pool')
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    @patch(fqname(Link))
    def test_add_and_run(self, link):
        link.interval.total_seconds.return_value = 0.02
        self.planner._refresh_interval = 0.02
        self.planner.add_link(link)

        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.04)
        link.transfer.assert_called()

        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    @patch(fqname(Link))
    def test_invalid_interval(self, link):
        link.interval.total_seconds.return_value = 0.1
        self.planner._refresh_interval = 0.2

        self.assertRaises(ScheduleIntervalError, self.planner.add_link, link)


    def _with_exception(self, link, catch_exceptions):
        logging.getLogger('databay').setLevel(logging.CRITICAL)
        self.planner = SchedulePlanner(catch_exceptions=catch_exceptions)
        link.transfer.side_effect = DummyException()
        link.interval.total_seconds.return_value = 0.02
        self.planner._refresh_interval = 0.02

        self.planner.add_link(link)

        ex = []

        # a nasty way to check if the exception was raised and to pass it back to main thread
        def handler():
            try:
                self.planner.start()
                ex.append(None)
            except Exception as e:
                ex.append(e)

        th = Thread(target=handler, daemon=True)
        th.start()
        time.sleep(0.04)
        link.transfer.assert_called()

        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

        if catch_exceptions:
            self.assertIsNone(ex[0], "Exception should not have propagated")
        else:
            self.assertIsInstance(ex[0], DummyException, "DummyException should have propagated")

    @patch(fqname(Link))
    def test_catch_exception(self, link):
        self._with_exception(link, True)

    @patch(fqname(Link))
    def test_raise_exception(self, link):
        self._with_exception(link, False)


