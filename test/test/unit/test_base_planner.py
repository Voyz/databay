import logging
from datetime import timedelta
from unittest import TestCase, mock
from unittest.mock import patch, MagicMock

import databay
from databay import BasePlanner, Link
from databay.errors import MissingLinkError
from test_utils import fqname


class TestBasePlanner(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.getLogger('databay').setLevel(logging.WARNING)

    @patch.multiple(BasePlanner,  __abstractmethods__=set())
    def setUp(self):
        self.planner = BasePlanner()
        self.planner._schedule = MagicMock(
            side_effect=lambda link: link.set_job(object()))
        self.planner._unschedule = MagicMock(
            side_effect=lambda link: link.set_job(None))
        self.planner._start_planner = MagicMock()
        self.planner._shutdown_planner = MagicMock()

    @patch(fqname(Link), spec=Link)
    def test_add_links(self, link):
        def set_job(job):
            link.job = job
        link.set_job.side_effect = set_job
        link.job = None

        self.planner.add_links(link)
        self.assertIsNotNone(link.job, 'Link should contain a job')
        self.assertTrue(link in self.planner.links,
                        'Planner should contain the link')

    @patch(fqname(Link), spec=Link)
    def test_add_links_array(self, link):
        def set_job(job):
            link.job = job
        link.set_job.side_effect = set_job
        link.job = None

        self.planner.add_links([link])
        self.assertIsNotNone(link.job, 'Link should contain a job')
        self.assertTrue(link in self.planner.links,
                        'Planner should contain the link')

    @patch(fqname(Link), spec=Link)
    def test_remove_links(self, link):
        def set_job(job):
            link.job = job
        link.set_job.side_effect = set_job
        link.job = None

        self.planner.add_links(link)
        self.planner.remove_links(link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertTrue(link not in self.planner.links,
                        'Planner should not contain the link')

    @patch(fqname(Link), spec=Link)
    def test_remove_invalid_link(self, link):
        def set_job(job):
            link.job = job
        link.set_job.side_effect = set_job
        link.job = None

        self.assertRaises(MissingLinkError, self.planner.remove_links, link)
        self.assertIsNone(link.job, 'Link should not contain a job')
        self.assertTrue(link not in self.planner.links,
                        'Planner should not contain the link')

    @patch(fqname(Link), spec=Link)
    def test_start(self, link):
        self.planner.add_links(link)
        self.planner.start()
        link.on_start.assert_called()
        self.planner._start_planner.assert_called()

    @patch(fqname(Link), spec=Link)
    def test_shutdown(self, link):
        self.planner.add_links(link)
        self.planner.shutdown()
        link.on_shutdown.assert_called()
        self.planner._shutdown_planner.assert_called()

    @patch(fqname(Link), spec=Link)
    def test_start_order(self, link):
        # on_start should be called before _start_planner
        link.on_start.side_effect = lambda: self.planner._start_planner.assert_not_called()

        self.planner.add_links(link)
        self.planner.start()

        # finally both should be called
        link.on_start.assert_called()
        self.planner._start_planner.assert_called()

    @patch(fqname(Link), spec=Link)
    def test_shutdown_order(self, link):
        # on_shutdown should be called after _shutdown_planner
        self.planner._shutdown_planner.side_effect = lambda wait: link.on_shutdown.assert_not_called()

        self.planner.add_links(link)
        self.planner.shutdown()

        # finally both should be called
        link.on_shutdown.assert_called()
        self.planner._shutdown_planner.assert_called()

    @patch(fqname(Link), spec=Link)
    def test_purge(self, link):
        self.planner.add_links(link)
        self.planner.purge()

        self.planner._unschedule.assert_called_with(link)
        self.assertEqual(self.planner.links, [])

    @patch(fqname(Link), spec=Link)
    def test_purge_while_running(self, link):
        self.planner.add_links(link)
        self.planner.start()
        self.planner.purge()

        self.planner._unschedule.assert_called_with(link)
        self.assertEqual(self.planner.links, [])

        self.planner.shutdown()
