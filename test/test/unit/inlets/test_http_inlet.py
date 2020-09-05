import asyncio
import logging
import sys

# if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
#     from unittest.mock import MagicMock, patch, AsyncMock
# else:
from asynctest import CoroutineMock, MagicMock, patch
# AsyncMock = CoroutineMock

from databay import Update
from databay.inlets import HttpInlet
from databay.misc import inlet_tester
from test_utils import fqname

logging.getLogger('databay.HttpInlet').setLevel(logging.WARNING)

client = MagicMock() # for ClientSession() as session
client_mock = CoroutineMock() # for session.get() as response


def set_response(payload):
    response = CoroutineMock(read=CoroutineMock(return_value=payload))
    client_mock.get.return_value.__aenter__.return_value = response
    client.return_value.__aenter__.return_value = client_mock

@patch('aiohttp.ClientSession', new=client)
class TestHttpInlet(inlet_tester.InletTester):

    def setUp(self):
        super().setUp()
        set_response(b'{"asdf":"12"}')

    def get_inlet(self):
        return HttpInlet('https://jsonplaceholder.typicode.com/todos/1')

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

        self.assertRaisesRegex(ValueError, 'Response does not contain valid JSON', asyncio.run, self.inlet._pull(update))

    @patch(fqname(Update))
    def test_invalid_html(self, update):
        set_response(None)
        self.inlet.json = False

        self.assertRaisesRegex(AttributeError, '\'NoneType\' object has no attribute \'decode\'', asyncio.run, self.inlet._pull(update))




