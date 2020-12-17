import logging
import os
import sys
import warnings
from unittest import TestCase, mock

from unittest.mock import patch, MagicMock
import asyncio
from importlib import reload

from databay import config
from test_utils import DummyException

_sys_version_info = sys.version_info


async def test_coroutine():
    return 123

def no_loop_error():
    raise RuntimeError('There is no current event loop')

def generic_error():
    raise RuntimeError('Dummy runtime error.')

test_loop = MagicMock()

class TestConfig(TestCase):

    # def setUp(self):
    #     logging.shutdown()
    #     reload(logging)

    @patch('sys.version_info')
    def test_event_loop_policy_3_8(self, version_info):
        if sys.platform != 'win32':
            self.skipTest('Only testable on Windows.')
        if _sys_version_info[0] >= 3 and _sys_version_info[1] <= 6:
            self.skipTest('Only testable on Python 3.7+')

        version_info.__getitem__.side_effect = lambda x: [3, 8][x]

        # fake a 3.8 default setup
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        reload(config)

        self.assertIsInstance(asyncio.get_event_loop_policy(), asyncio.WindowsSelectorEventLoopPolicy,
                              "Asyncio event loop policy should be WindowsSelectorEventLoopPolicy.")

    @patch('sys.version_info')
    def test_event_loop_policy_3_7(self, version_info):
        if sys.platform != 'win32':
            self.skipTest('Only testable on Windows')

        if _sys_version_info[0] >= 3 and _sys_version_info[1] <= 6:
            self.skipTest('Only testable on Python 3.7+')

        version_info.__getitem__.side_effect = lambda x: [3, 7][x]

        # fake a manual 3.8 default setup
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        reload(config)

        self.assertIsInstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy,
                              "Asyncio event loop policy should be WindowsProactorEventLoopPolicy.")

    @patch('databay.config.sys.platform', 'win32')
    @patch('databay.config.sys.stdout', MagicMock(encoding='windows-1252'))
    @patch('databay.config.sys.stdin', MagicMock(encoding='windows-1252'))
    # disable stream handler
    @patch('logging.StreamHandler.emit', lambda x, y: None)
    def test_windows_1252(self):
        with self.assertLogs(logging.getLogger('databay'), level='WARNING') as cm:
            config.initialise()
            self.assertTrue(
                'stdin or stdout encoder is set to \'windows-1252\'' in ';'.join(cm.output))

    @patch('databay.config.sys.platform', 'win32')
    @patch('databay.config.sys.stdout', MagicMock(encoding='utf-8'))
    @patch('databay.config.sys.stdin', MagicMock(encoding='utf-8'))
    def test_not_windows_1252(self):
        databay_logger = logging.getLogger('databay')
        temp = databay_logger.warning
        databay_logger.warning = MagicMock()
        config.initialise()
        self.assertTrue(
            'stdin or stdout encoder is set to \'windows-1252\'' not in databay_logger.warning.call_args_list)
        databay_logger.warning = temp

    @patch('databay.config.sys.platform', 'win32')
    @patch('databay.config.sys.stdout', MagicMock(encoding='windows-1252'))
    @patch('databay.config.sys.stdin', MagicMock(encoding='windows-1252'))
    # @patch('logging.Logger.warning')
    @mock.patch.dict(os.environ, {"DATABAY_IGNORE_WARNINGS": "windows-1252"})
    def test_windows_1252_ignored(self):
        temp = logging.Logger.warning
        warning = logging.Logger.warning = MagicMock()
        config.initialise()
        string_args = ';'.join([str(call[0][0])
                                for call in warning.call_args_list])
        self.assertTrue('stdin or stdout encoder is set to \'windows-1252\'' not in string_args,
                        'Should not contain windows-1252 warning')
        logging.Logger.warning = temp

    @patch('databay.config.sys.platform', 'win32')
    @patch('databay.config.sys.stdout', MagicMock(encoding='windows-1252'))
    @patch('databay.config.sys.stdin', MagicMock(encoding='windows-1252'))
    @mock.patch.dict(os.environ, {"DATABAY_IGNORE_WARNINGS": "test_ignore"})
    # disable stream handler
    @patch('logging.StreamHandler.emit', lambda x, y: None)
    def test_windows_1252_incorrect_ignore(self):
        with self.assertLogs(logging.getLogger('databay'), level='WARNING') as cm:
            config.initialise()
            self.assertTrue('stdin or stdout encoder is set to \'windows-1252\'' in ';'.join(cm.output))


    @patch('sys.version_info')
    @patch('asyncio.get_event_loop', MagicMock(return_value=test_loop))
    def test_asyncio_monkey_patch(self, version_info):
        version_info.__getitem__.side_effect = lambda x: [3, 6][x]

        config.initialise()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            coro = test_coroutine()
            asyncio.run(coro)

            asyncio.get_event_loop.assert_called()
            test_loop.run_until_complete.assert_called_with(coro)

    @patch('sys.version_info')
    @patch('asyncio.get_event_loop', MagicMock(side_effect=no_loop_error))
    @patch('asyncio.new_event_loop', MagicMock(return_value=test_loop))
    @patch('asyncio.set_event_loop',MagicMock())
    def test_asyncio_monkey_patch_no_loop(self, version_info):
        version_info.__getitem__.side_effect = lambda x: [3, 6][x]

        config.initialise()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            coro = test_coroutine()
            asyncio.run(coro)

            asyncio.get_event_loop.assert_called()
            asyncio.new_event_loop.assert_called()
            asyncio.set_event_loop.assert_called_with(test_loop)
            test_loop.run_until_complete.assert_called_with(coro)

    @patch('sys.version_info')
    @patch('asyncio.get_event_loop', MagicMock(side_effect=generic_error))
    def test_asyncio_monkey_patch_other_error(self, version_info):
        version_info.__getitem__.side_effect = lambda x: [3, 6][x]

        async def coroutine():
            return 123

        config.initialise()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            self.assertRaises(RuntimeError, asyncio.run, coroutine())
