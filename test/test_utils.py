import sys


def fqname(obj):
    return ".".join([obj.__module__, obj.__name__])


class DummyException(Exception):
    """ Raised when they add coriander to all your food."""

    def __init__(self, message="I'm a dummy exception"):
        self.message = message
        super().__init__(self.message)


class DummyUnusualException(Exception):
    """ Raised when they add parsley to all your food."""

    def __init__(self, argA: int, argB: bool):
        super().__init__(f'{argA}, {argB}, I\'m an unusual dummy exception')


if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
    from unittest.mock import AsyncMock
    CoroutineMock = AsyncMock
else:
    from asynctest import CoroutineMock

def pull_mock(rv=None):
    if rv is None:
        rv = [object()]

    async def pull_coro(_):
        return rv

    return CoroutineMock(side_effect=pull_coro)
