"""
.. warning::
    :any:`HttpInlet` requires `AIOHTTP <https://docs.aiohttp.org/en/stable/>`_ to function. Please install required dependencies using:

    .. code-block:: python

        pip install "databay[HttpInlet]"
"""

import json
import logging
from json import JSONDecodeError
from typing import List, Union

import aiohttp
import ssl

from databay.inlet import Inlet
from databay import Record

_LOGGER = logging.getLogger('databay.HttpInlet')

class HttpInlet(Inlet):
    """
    Inlet for pulling data from a specified URL using `aiohttp <aiohttp.ClientSession.get_>`__.

    .. _aiohttp.ClientSession.get: https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession.get
    """

    def __init__(self, url:str, json:str=True, cacert=None, params=None, *args, **kwargs):
        """
        :type url: str
        :param url: URL that should be queried for data.

        :type json: bool
        :param json: Whether response should be parsed as JSON.
        """
        self.tcp_connector = None
        super().__init__(*args, **kwargs)
        self.url = url
        self.json = json
        self.cacert = cacert
        self.params = params

        if self.cacert is not None and self.cacert != False:
            context = ssl.create_default_context()
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_verify_locations(self.cacert)
            self.context = context
            self.tcp_connector = aiohttp.TCPConnector(ssl_context=self.context)

    async def pull(self, update) -> Union[List[Record], str]:
        """
        Asynchronously pulls data from the specified URL using aiohttp.ClientSession.get_

        :type update: :any:`Update`
        :param update: Update object representing the particular Link transfer.

        :return: Single or multiple records produced.
        :rtype: :any:`Record` or list[:any:`Record`]
        """
        _LOGGER.info(f'{update} pulling {self.url}')
        async with aiohttp.ClientSession(connector=self.tcp_connector) as session:
            async with session.get(self.url, params=self.params) as response:
                payload = await response.read()
                _LOGGER.info(f'{update} received {self.url}')
                try:
                    if self.json:
                        return json.loads(payload)
                    else:
                        return payload.decode("utf-8")
                except Exception as e:
                    if isinstance(e, JSONDecodeError) and 'Expecting value: line 1 column 1 (char 0)' in str(e):
                        raise ValueError(f'Response does not contain valid JSON:\n\n{payload}') from e
                    else:
                        raise e

    def __repr__(self):
        s = "%s(" % (self.__class__.__name__)

        s += f'url={self.url}'

        if self.metadata:
            s += ', metadata:%s' % self.metadata

        s += ')'
        return s


