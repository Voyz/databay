"""
.. warning::
    :any:`HttpInlet` requires `AIOHTTP <https://docs.aiohttp.org/en/stable/>`_ to function. Please install required dependencies using:

    .. code-block:: python

        pip install databay[HttpInlet]
"""

import json
import logging
from typing import List

import aiohttp

from databay.inlet import Inlet
from databay import Record

_LOGGER = logging.getLogger('databay.HttpInlet')

class HttpInlet(Inlet):
    """
    Inlet for pulling data from a specified URL using `aiohttp <aiohttp.ClientSession.get_>`__.

    .. _aiohttp.ClientSession.get: https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession.get
    """

    def __init__(self, url:str, *args, **kwargs):
        """
        :type url: str
        :param url: URL that should be queried for data.
        """
        super().__init__(*args, **kwargs)
        self.url = url

    async def pull(self, update) -> List[Record]:
        """
        Asynchronously pulls data from the specified URL using aiohttp.ClientSession.get_

        :type update: :any:`Update`
        :param update: Update object representing the particular Link transfer.

        :return: Single or multiple records produced.
        :rtype: :any:`Record` or list[:any:`Record`]
        """
        _LOGGER.info(f'{update} pulling {self.url}')
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                payload = await response.read()
                record = self.new_record(payload=json.loads(payload))
                _LOGGER.info(f'{update} received {self.url}')
                return [record]


