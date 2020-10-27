import logging
import time
from threading import Thread
from unittest import TestCase
from unittest.mock import MagicMock

from apscheduler.schedulers import SchedulerAlreadyRunningError, SchedulerNotRunningError
from apscheduler.schedulers.base import STATE_RUNNING, STATE_STOPPED, STATE_PAUSED

import databay
from databay import Link
from databay.errors import MissingLinkError
from databay.planners.aps_planner import ApsPlanner
from test_utils import fqname, DummyException, DummyUnusualException


class TestApsPlanner(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.getLogger('databay').setLevel(logging.WARNING)

    def setUp(self):
        self.planner = ApsPlanner()

        link = MagicMock(spec=Link)

        def set_job(job):
            link.job = job

        link.interval.total_seconds.return_value = 0.02
        link.set_job.side_effect = set_job
        link.job = None
        self.link = link


    def test__schedule(self):
        self.planner._schedule(self.link)
        self.assertIsNotNone(self.link.job, 'Link should contain a job')
        asp_job = self.planner._scheduler.get_jobs()[0]
        self.assertEqual(self.link.job, asp_job, 'Link\'s job should be same as scheduler\'s')

    def test__unschedule(self):
        self.planner._schedule(self.link)
        self.planner._unschedule(self.link)
        self.assertIsNone(self.link.job, 'Link should not contain a job')
        self.assertEqual(len(self.planner._scheduler.get_jobs()), 0, 'Scheduler should not have any jobs')

    def test__unschedule_invalid(self):
        self.planner._unschedule(self.link)
        self.assertIsNone(self.link.job, 'Link should not contain a job')
        self.assertEqual(len(self.planner._scheduler.get_jobs()), 0, 'Scheduler should not have any jobs')


    def test_add_links(self):
        self.planner.add_links(self.link)
        self.assertIsNotNone(self.link.job, 'Link should contain a job')
        self.assertTrue(self.link in self.planner.links, 'Planner should contain the link')

    def test_add_links_on_init(self):
        self.planner = ApsPlanner(self.link)
        self.assertIsNotNone(self.link.job, 'Link should contain a job')
        self.assertTrue(self.link in self.planner.links, 'Planner should contain the link')

    def test_remove_links(self):
        self.planner.add_links(self.link)
        self.planner.remove_links(self.link)
        self.assertIsNone(self.link.job, 'Link should not contain a job')
        self.assertTrue(self.link not in self.planner.links, 'Planner should not contain the link')

    def test_remove_invalid_link(self):
        self.assertRaises(MissingLinkError, self.planner.remove_links, self.link)
        self.assertIsNone(self.link.job, 'Link should not contain a job')
        self.assertTrue(self.link not in self.planner.links, 'Planner should not contain the link')

    def test_start(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.assertTrue(self.planner.running, 'Scheduler should be running')
        self.planner.shutdown(wait=False)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    # todo: APS is currently broken for this test case, wait for an update
    def xtest_start_paused(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.pause()
        self.assertRaises(SchedulerAlreadyRunningError, self.planner.start)
        self.assertEqual(self.planner._scheduler.state, STATE_PAUSED, 'Scheduler should be paused')
        self.planner.shutdown(wait=False)

        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown(wait=False)
        self.assertFalse(self.planner.running, 'Scheduler should not be running')
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_pause(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.pause()
        self.assertEqual(self.planner._scheduler.state, STATE_PAUSED, 'Scheduler should be paused')
        self.planner.shutdown(wait=False)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_resume(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.pause()
        self.assertEqual(self.planner._scheduler.state, STATE_PAUSED, 'Scheduler should be paused')
        self.planner.resume()
        self.assertTrue(self.planner.running, 'Scheduler should not be paused')
        self.planner.shutdown(wait=False)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_shutdown_paused(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.pause()
        self.assertEqual(self.planner._scheduler.state, STATE_PAUSED, 'Scheduler should be paused')
        self.planner.shutdown(wait=False)
        self.assertFalse(self.planner.running, 'Scheduler should not be running')
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_pause_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown(wait=False)
        self.assertRaises(SchedulerNotRunningError, self.planner.pause)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_resume_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown(wait=False)
        self.assertRaises(SchedulerNotRunningError, self.planner.resume)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_start_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown(wait=False)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread 1 should be stopped.')
        self.assertFalse(self.planner.running, 'Scheduler should not be running')

        th2 = Thread(target=self.planner.start, daemon=True)
        th2.start()
        self.assertTrue(self.planner.running, 'Scheduler should be running')
        self.planner.shutdown(wait=False)
        th2.join(timeout=2)
        self.assertFalse(th2.is_alive(), 'Thread 2 should be stopped.')


    def test_add_and_run(self):
        self.link.interval.total_seconds.return_value = 0.02
        self.planner.add_links(self.link)

        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.04)
        self.link.transfer.assert_called()

        self.planner.shutdown(wait=False)
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')


    def _with_exception(self, link, catch_exceptions):
        logging.getLogger('databay').setLevel(logging.CRITICAL)
        # logging.getLogger('databay').setLevel(logging.INFO)
        self.planner = ApsPlanner(catch_exceptions=catch_exceptions)

        link.transfer.side_effect = DummyException()
        link.interval.total_seconds.return_value = 0.02
        self.planner.add_links(link)

        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.04)
        link.transfer.assert_called()

        if catch_exceptions:
            self.assertTrue(self.planner.running, 'Scheduler should be running')
            self.planner.shutdown(wait=False)
            th.join(timeout=2)
            self.assertFalse(th.is_alive(), 'Thread should be stopped.')

        self.assertFalse(self.planner.running, 'Scheduler should be stopped')


    def test_catch_exception(self):
        self._with_exception(self.link, True)


    def test_raise_exception(self):
        self._with_exception(self.link, False)

    def test_uncommon_exception(self):
        logging.getLogger('databay').setLevel(logging.CRITICAL)

        self.link.transfer.side_effect = DummyUnusualException(123, True)
        self.link.interval.total_seconds.return_value = 0.02
        self.planner.add_links(self.link)

        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.04)
        self.link.transfer.assert_called()

        self.assertFalse(self.planner.running, 'Scheduler should be stopped')

    def test_purge(self):
        self.link.interval.total_seconds.return_value = 0.02
        self.planner.add_links(self.link)
        self.planner.purge()

        self.link.set_job.assert_called_with(None)
        self.assertEqual(self.planner.links, [])


    def test_purge_while_running(self):
        self.planner.add_links(self.link)
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.purge()

        self.link.set_job.assert_called_with(None)
        self.assertEqual([], self.planner.links)
        self.assertEqual([], self.planner._scheduler.get_jobs())

        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_purge_after_shutdown(self):
        self.planner.add_links(self.link)
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown()
        self.planner.purge()

        self.link.set_job.assert_called_with(None)
        self.assertEqual([], self.planner.links)
        self.assertEqual([], self.planner._scheduler.get_jobs())

        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')
