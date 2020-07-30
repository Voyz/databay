import importlib

if importlib.util.find_spec('aiohttp') is not None:
    from databay.inlets.http_inlet import HttpInlet

from databay.inlets.random_int_inlet import RandomIntInlet