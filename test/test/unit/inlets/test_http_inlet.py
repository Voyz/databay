import asyncio
import logging

from asynctest import CoroutineMock, MagicMock, patch

from databay.inlets import HttpInlet
from databay.misc import inlet_tester

logging.getLogger('databay.HttpInlet').setLevel(logging.WARNING)

client = MagicMock() # for ClientSession() as session
client_mock = CoroutineMock() # for session.get() as response

response = CoroutineMock(read=CoroutineMock(return_value='{"asdf":"12"}'))
client_mock.get.return_value.__aenter__.return_value = response
client.return_value.__aenter__.return_value = client_mock


@patch('aiohttp.ClientSession', new=client)
class TestHttpInlet(inlet_tester.InletTester):


    def get_inlet(self):
        return HttpInlet('https://jsonplaceholder.typicode.com/todos/1')

    def test_test(self):
        asyncio.run(self.inlet.pull(None))




