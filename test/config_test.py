import sys

if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
    from unittest.mock import mock, patch, CoroutineMock, MagicMock

else:
    from asynctest import mock, patch, CoroutineMock, MagicMock
