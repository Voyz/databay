import os
import sys
import asyncio

# Fix for #3 - Asyncio/aiohttp causes a 'RuntimeError: Event loop is closed' error on ProactorEventLoop, which became default for Python 3.8
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

IGNORE_WARNINGS = []


def initialise():
    import logging

    from databay.misc.logs import ISO8601Formatter

    iso8601_formatter = ISO8601Formatter(
        '%(asctime)s|%(levelname)-.1s| %(message)s (%(name)s)', millis_precision=3)  # / %(threadName)s)')
    iso8601_formatter.set_pretty(True)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(iso8601_formatter)

    default_logger = logging.getLogger('databay')
    default_logger.addHandler(stream_handler)

    default_logger.setLevel(logging.WARNING)

    global IGNORE_WARNINGS
    IGNORE_WARNINGS = os.environ.get('DATABAY_IGNORE_WARNINGS', '').split(';')

    if sys.platform.startswith('win') and \
        (sys.stdin.encoding == 'windows-1252' or sys.stdout.encoding == 'windows-1252') and \
            'windows-1252' not in IGNORE_WARNINGS:
        default_logger.warning('stdin or stdout encoder is set to \'windows-1252\'. This may cause errors with data streaming. Fix by setting following environment variables: \n\nPYTHONIOENCODING=utf-8\nPYTHONLEGACYWINDOWSSTDIO=utf-8\n\nSet DATABAY_IGNORE_WARNINGS=\'windows-1252\' to ignore this warning.')

    # monkey patch on asyncio.run for Python versions below 3.7.
    if sys.version_info[0] >= 3 and sys.version_info[1] <= 6:
        def asyncio_run_monkey_patch(task):
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError as e:
                if "There is no current event loop" in str(e):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                else:
                    raise e
            return loop.run_until_complete(task)

        asyncio.run = asyncio_run_monkey_patch
