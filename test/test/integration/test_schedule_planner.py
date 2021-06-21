import logging
import time
from threading import Thread
from unittest import TestCase
from unittest.mock import MagicMock

import schedule

import databay
from databay import Link
from databay.errors import MissingLinkError
from databay.planners import SchedulePlanner
from databay.planners.schedule_planner import ScheduleIntervalError
from test_utils import fqname, DummyException, DummyUnusualException


class TestSchedulePlanner(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.getLogger('databay').setLevel(logging.WARNING)

    def setUp(self):
        self.planner = SchedulePlanner(refresh_interval=0.02)

        link = MagicMock(spec=Link)

        def set_job(job):
            link.job = job

        link.interval.total_seconds.return_value = 0.02
        link.set_job.side_effect = set_job
        link.job = None
        link.immediate_transfer = True
        self.link = link

    def tearDown(self):
        if len(schedule.jobs) > 0:
            schedule.clear()

    def test__run_job(self):
        self.planner._create_thread_pool()
        self.planner._run_job(self.link)
        self.link.transfer.assert_called_once()
        self.planner._destroy_thread_pool()

    def test__schedule(self):
        self.planner._schedule(self.link)
        self.assertIsNotNone(self.link.job, 'Link should contain a job')
        schedule_job = schedule.jobs[0]
        self.assertEqual(self.link.job, schedule_job,
                         'Link\'s job should be same as schedule\'s')
        # self.planner._unschedule(link)

    def test__unschedule(self):
        self.planner._schedule(self.link)
        self.planner._unschedule(self.link)
        self.assertIsNone(self.link.job, 'Link should not contain a job')
        self.assertEqual(len(schedule.jobs), 0,
                         'Schedule should not have any jobs')

    def test__unschedule_invalid(self):
        self.planner._unschedule(self.link)
        self.assertIsNone(self.link.job, 'Link should not contain a job')
        self.assertEqual(len(schedule.jobs), 0,
                         'Scheduler should not have any jobs')

    def test_add_links(self):
        self.planner.add_links(self.link)
        self.assertIsNotNone(self.link.job, 'Link should contain a job')
        self.assertTrue(self.link in self.planner.links,
                        'Planner should contain the link')

    def test_add_links_on_init(self):
        self.planner = SchedulePlanner(self.link, refresh_interval=0.02)
        self.assertIsNotNone(self.link.job, 'Link should contain a job')
        self.assertTrue(self.link in self.planner.links,
                        'Planner should contain the link')

    def test_remove_links(self):
        self.planner.add_links(self.link)
        self.planner.remove_links(self.link)
        self.assertIsNone(self.link.job, 'Link should not contain a job')
        self.assertTrue(self.link not in self.planner.links,
                        'Planner should not contain the link')

    def test_remove_invalid_link(self):
        self.assertRaises(MissingLinkError,
                          self.planner.remove_links, self.link)
        self.assertIsNone(self.link.job, 'Link should not contain a job')
        self.assertTrue(self.link not in self.planner.links,
                        'Planner should not contain the link')

    def test_start(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.assertTrue(self.planner._running, 'Planner should be running')
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_start_when_already_running(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.assertTrue(self.planner._running, 'Planner should be running')
        th2 = Thread(target=self.planner.start, daemon=True)
        th2.start()
        self.assertFalse(th2.is_alive(), 'Starting again should instantly exit.')
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_shutdown(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.shutdown()
        self.assertFalse(self.planner._running,
                         'Planner should be not running')
        self.assertIsNone(self.planner._thread_pool,
                          'Planner should not have a thread pool')
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_add_and_run(self):
        self.link.interval.total_seconds.return_value = 0.02
        self.planner._refresh_interval = 0.02
        self.planner.add_links(self.link)

        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.04)
        self.link.transfer.assert_called()

        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_invalid_interval(self):
        self.link.interval.total_seconds.return_value = 0.1
        self.planner._refresh_interval = 0.2

        self.assertRaises(ScheduleIntervalError,
                          self.planner.add_links, self.link)

    def _with_exception(self, link, ignore_exceptions):
        self.planner = SchedulePlanner(ignore_exceptions=ignore_exceptions)
        self.planner.immediate_transfer = False # otherwise planner will never start
        link.transfer.side_effect = DummyException()
        link.interval.total_seconds.return_value = 0.02
        self.planner._refresh_interval = 0.02

        link.transfer.side_effect = DummyException()
        link.interval.total_seconds.return_value = 0.02
        self.planner.add_links(link)

        with self.assertLogs(logging.getLogger('databay.BasePlanner'), level='WARNING') as cm:

            th = Thread(target=self.planner.start, daemon=True)
            th.start()
            time.sleep(0.04)
            link.transfer.assert_called()

            if ignore_exceptions:
                self.assertTrue(self.planner.running,
                                'Planner should be running')
                self.planner.shutdown(wait=False)
                th.join(timeout=2)
                self.assertFalse(th.is_alive(), 'Thread should be stopped.')

            self.assertFalse(self.planner.running, 'Planner should be stopped')
            self.assertTrue(
                'I\'m a dummy exception' in ';'.join(cm.output))

    def test_ignore_exception(self):
        self._with_exception(self.link, True)

    def test_raise_exception(self):
        self._with_exception(self.link, False)

    def test_uncommon_exception(self):

        self.link.transfer.side_effect = DummyUnusualException(
            argA=123, argB=True)
        self.link.interval.total_seconds.return_value = 0.02
        self.planner.add_links(self.link)

        with self.assertLogs(logging.getLogger('databay.BasePlanner'), level='WARNING') as cm:

            th = Thread(target=self.planner.start, daemon=True)
            th.start()
            time.sleep(0.04)
            self.link.transfer.assert_called()

            self.assertFalse(self.planner.running, 'Scheduler should be stopped')
            self.assertTrue(
                '123, True, I\'m an unusual dummy exception' in ';'.join(cm.output))

    def test_purge(self):
        self.link.interval.total_seconds.return_value = 0.02
        self.planner.add_links(self.link)
        self.planner.purge()

        self.link.set_job.assert_called_with(None)
        self.assertEqual(self.planner.links, [])
        self.assertEqual(schedule.jobs, [])

    def test_purge_while_running(self):
        self.planner.add_links(self.link)
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.planner.purge()

        self.link.set_job.assert_called_with(None)
        self.assertEqual(self.planner.links, [])
        self.assertEqual(schedule.jobs, [])

        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_start_when_already_running(self):
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        self.assertTrue(self.planner._running, 'Planner should be running')
        th2 = Thread(target=self.planner._start_planner, daemon=True)
        th2.start() # this shouldn't do anything as we're already running
        th2.join()
        self.assertFalse(th2.is_alive(), 'Second start thread should have exited.')
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_immediate_transfer(self):
        self.link.interval.total_seconds.return_value = 10
        self.planner.add_links(self.link)
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.01)
        self.link.transfer.assert_called_once()
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')

    def test_immediate_transfer_exception(self):
        self.link.interval.total_seconds.return_value = 10
        self.planner._ignore_exceptions = False
        self.link.transfer.side_effect = DummyException('First transfer exception!')
        self.planner.add_links(self.link)
        with self.assertLogs(logging.getLogger('databay.BasePlanner'), level='WARNING') as cm:
            th = Thread(target=self.planner.start, daemon=True)
            th.start()
            self.link.transfer.assert_called_once()
            self.assertFalse(self.planner.running, 'Planner should not have started')
            th.join(timeout=2)
            self.assertFalse(th.is_alive(), 'Thread should be stopped.')
            self.assertTrue(
                'First transfer exception!' in ';'.join(cm.output))


    def test_immediate_transfer_off(self):
        self.link.interval.total_seconds.return_value = 10
        self.planner.immediate_transfer = False
        self.planner.add_links(self.link)
        th = Thread(target=self.planner.start, daemon=True)
        th.start()
        time.sleep(0.01)
        self.link.transfer.assert_not_called()
        self.planner.shutdown()
        th.join(timeout=2)
        self.assertFalse(th.is_alive(), 'Thread should be stopped.')