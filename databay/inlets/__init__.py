import importlib.util

if importlib.util.find_spec('aiohttp') is not None:
    from databay.inlets.http_inlet import HttpInlet
else: # pragma: no cover
    def HttpInlet(*args, **kwargs):
        raise ImportError('aiohttp dependency is required for HttpInlet. Fix by running: pip install databay[HttpInlet]')

from databay.inlets.random_int_inlet import RandomIntInlet
from databay.inlets.null_inlet import NullInlet