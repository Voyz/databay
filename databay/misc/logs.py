import logging
import time


class ISO8601Formatter(logging.Formatter):

    def __init__(self, *args, millis_precision=3, pretty=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.millis_precision = millis_precision
        self.precision_mult = 10 ** (self.millis_precision-3)
        self.pretty = pretty
        self.str_format = "%s.%0" + str(self.millis_precision) + "d%s"

        self.make_time_format()

    def make_time_format(self):
        if self.pretty:
            self.time_format = '%Y-%m-%d %H:%M:%S'
        else:
            self.time_format = '%Y-%m-%dT%H:%M:%S'

    def set_pretty(self, pretty):
        self.pretty = pretty
        self.make_time_format()

    def formatTime(self, record, datefmt=None):  # pragma: no cover
        ct = self.converter(record.created)
        t = time.strftime(self.time_format, ct)
        tz = time.strftime('%z', ct)

        if self.pretty:
            tz = ''

        msecs = record.msecs * self.precision_mult
        s = self.str_format % (t, msecs, tz)
        return s
