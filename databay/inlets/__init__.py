import importlib

if importlib.util.find_spec('aiohttp') is not None:
    from databay.inlets.http_inlet import HttpInlet
else:
    def HttpInlet(*args, **kwargs):
        raise ModuleNotFoundError('aiohttp dependency is required for HttpInlet. Fix by running: pip install databay[HttpInlet]')

from databay.inlets.random_int_inlet import RandomIntInlet