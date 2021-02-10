import asyncio
import logging
import ssl
import sys

from unittest.mock import patch

import aiohttp

if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
    from unittest.mock import AsyncMock, MagicMock
    CoroutineMock = AsyncMock
else:
    from asynctest import CoroutineMock, MagicMock

from databay import Update
from databay.inlets import HttpInlet
from databay.misc import inlet_tester
from test_utils import fqname

logging.getLogger('databay.HttpInlet').setLevel(logging.WARNING)

client = MagicMock()  # for ClientSession() as session
client_mock = CoroutineMock()  # for session.get() as response

create_default_context_mock = MagicMock(spec=ssl.SSLContext)

_TEST_URL = 'https://jsonplaceholder.typicode.com/todos/1'


def set_response(payload):
    response = CoroutineMock(read=CoroutineMock(return_value=payload))
    get_mock = MagicMock()
    get_mock.return_value.__aenter__.return_value = response
    client_mock.get = get_mock
    client.return_value.__aenter__.return_value = client_mock


@patch('aiohttp.ClientSession', new=client)
class TestHttpInlet(inlet_tester.InletTester):

    def setUp(self):
        super().setUp()
        set_response(b'{"asdf":"12"}')

    def get_inlet(self):
        return HttpInlet(_TEST_URL)

    @patch(fqname(Update))
    def test_json(self, update):
        records = asyncio.run(self.inlet._pull(update))

        self.assertIsInstance(records, (list))

    @patch(fqname(Update))
    def test_html(self, update):
        self.inlet.json = False

        records = asyncio.run(self.inlet._pull(update))

        self.assertIsInstance(records, (list))

    @patch(fqname(Update))
    def test_invalid_json(self, update):
        set_response(b'<html>')
        self.inlet.json = True

        self.assertRaisesRegex(
            ValueError, 'Response does not contain valid JSON', asyncio.run, self.inlet._pull(update))

    @patch(fqname(Update))
    def test_invalid_html(self, update):
        set_response(None)
        self.inlet.json = False

        self.assertRaisesRegex(AttributeError,
                               '\'NoneType\' object has no attribute \'decode\'', asyncio.run, self.inlet._pull(update))

    def test_cacert_false(self):
        inlet = HttpInlet(_TEST_URL, cacert=False)
        self.assertIsNone(inlet.tcp_connector)

    def test_cacert_none(self):
        inlet = HttpInlet(_TEST_URL, cacert=None)
        self.assertIsNone(inlet.tcp_connector)

    @patch(fqname(Update))
    @patch('ssl.create_default_context', return_value=create_default_context_mock)
    def test_cacert(self, _, update):
        cacert = '/some/path/to/cacert.pem'
        inlet = HttpInlet(_TEST_URL, cacert=cacert)
        asyncio.run(inlet._pull(update))
        self.assertIsNotNone(inlet.tcp_connector)
        self.assertIsInstance(inlet.tcp_connector, aiohttp.TCPConnector)
        create_default_context_mock.load_verify_locations.assert_called_with(cacert)

    @patch(fqname(Update))
    def test_params_none(self, update):
        inlet = HttpInlet(_TEST_URL, params=None)
        asyncio.run(inlet._pull(update))
        client_mock.get.assert_called_with(_TEST_URL, params=None)

    @patch(fqname(Update))
    def test_params(self, update):
        params = {'foo': 'bar'}
        inlet = HttpInlet(_TEST_URL, params=params)
        asyncio.run(inlet._pull(update))
        client_mock.get.assert_called_with(_TEST_URL, params=params)

    @patch(fqname(Update))
    def test_headers(self, update):
        headers = {'foo': 'bar'}
        inlet = HttpInlet(_TEST_URL, headers=headers)
        asyncio.run(inlet._pull(update))
        client.assert_called_with(connector=None, headers=headers)



