import logging
import time
from datetime import timedelta
from threading import Thread
from unittest import TestCase
from unittest.mock import patch

from apscheduler.schedulers import SchedulerAlreadyRunningError, SchedulerNotRunningError
from apscheduler.schedulers.base import STATE_RUNNING, STATE_STOPPED, STATE_PAUSED

import databay
from databay import Link
from databay.errors import MissingLinkError
from databay.planners.aps_planner import APSPlanner
from stubs.LinkStub import LinkStub
from test_utils import fqname, DummyException


class TestAPSPlanner(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.getLogger('databay').setLevel(logging.WARNING)

    def setUp(self):
        self.planner = APSPlanner()

    def test__schedule(self):
        link = LinkStub([], [], timedelta(seconds=1))
        self.planner._schedule(link)
        self.assertIsNotNone(link.job, 'Link should contain a job')
        asp_job = self.planner._scheduler.get_jobs()[0]
        self.assertEqual(link.job, asp_job, 'Link\'s job should be same as scheduler\'s')

    def test__unschedule(self):
        link = LinkStub([], [], timedelta(seconds=1))
        self.planner._schedule(link)
        self.planner._unschedule(link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertEqual(len(self.planner._scheduler.get_jobs()), 0, 'Scheduler should not have any jobs')

    def test__unschedule_invalid(self):
        link = LinkStub([], [], timedelta(seconds=1))
        # self.planner._schedule(link)
        self.planner._unschedule(link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertEqual(len(self.planner._scheduler.get_jobs()), 0, 'Scheduler should not have any jobs')


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
        # self.planner.add_link(link)
        self.assertRaises(MissingLinkError, self.planner.remove_link, link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertTrue(link not in self.planner.links, 'Planner should not contain the link')


    def test_start(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.assertTrue(self.planner.running, 'Scheduler should be running')
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    # todo: APS is currently broken for this test case, wait for an update
    def xtest_start_paused(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.pause()
        self.assertRaises(SchedulerAlreadyRunningError, self.planner.start)
        self.assertEqual(self.planner._scheduler.state, STATE_PAUSED, 'Scheduler should be paused')
        self.planner.shutdown()

        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown()
        self.assertFalse(self.planner.running, 'Scheduler should not be running')
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_pause(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.pause()
        self.assertEqual(self.planner._scheduler.state, STATE_PAUSED, 'Scheduler should be paused')
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_resume(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.pause()
        self.assertEqual(self.planner._scheduler.state, STATE_PAUSED, 'Scheduler should be paused')
        self.planner.resume()
        self.assertTrue(self.planner.running, 'Scheduler should not be paused')
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_shutdown_paused(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.pause()
        self.assertEqual(self.planner._scheduler.state, STATE_PAUSED, 'Scheduler should be paused')
        self.planner.shutdown()
        self.assertFalse(self.planner.running, 'Scheduler should not be running')
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_pause_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown()
        self.assertRaises(SchedulerNotRunningError, self.planner.pause)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_resume_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown()
        self.assertRaises(SchedulerNotRunningError, self.planner.resume)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_start_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread 1 should be stopped.')
        self.assertFalse(self.planner.running, 'Scheduler should not be running')

        th2 = Thread(target=self.planner.start, daemon=True)
        th2.start()
        self.assertTrue(self.planner.running, 'Scheduler should be running')
        self.planner.shutdown()
        th2.join(timeout=2)
        self.assertFalse(th2.is_alive(), 'Thread 2 should be stopped.')

    @patch(fqname(Link))
    def test_add_and_run(self, link):
        link.interval.total_seconds.return_value = 0.02
        self.planner.add_link(link)

        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.04)
        link.transfer.assert_called()

        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')


    def _with_exception(self, link, catch_exceptions):
        logging.getLogger('databay').setLevel(logging.CRITICAL)
        self.planner = APSPlanner(catch_exceptions=catch_exceptions)

        link.transfer.side_effect = DummyException()
        link.interval.total_seconds.return_value = 0.02
        self.planner.add_link(link)

        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.04)
        link.transfer.assert_called()

        if catch_exceptions:
            self.assertTrue(self.planner.running, 'Scheduler should be running')
            self.planner.shutdown()
            th.join(timeout=2)
            self.assertFalse(th.is_alive(), 'Thread should be stopped.')

        self.assertFalse(self.planner.running, 'Scheduler should be stopped')

    @patch(fqname(Link))
    def test_catch_exception(self, link):
        self._with_exception(link, True)

    @patch(fqname(Link))
    def test_raise_exception(self, link):
        self._with_exception(link, False)
