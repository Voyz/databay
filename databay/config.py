def initialise():
    import logging

    from databay.misc.logs import ISO8601Formatter


    iso8601_formatter = ISO8601Formatter('%(asctime)s|%(levelname)-.1s| %(message)s (%(name)s)', millis_precision=3)# / %(threadName)s)')
    iso8601_formatter.set_pretty(True)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(iso8601_formatter)

    default_logger = logging.getLogger('databay')
    default_logger.addHandler(stream_handler)

    logging.getLogger('databay').setLevel(logging.DEBUG)
