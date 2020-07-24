from datetime import timedelta

from databay.link import Link


class LinkStub(Link):
    def __init__(self, inlets:[], outlets:[], interval:timedelta, name:str='', catch_exceptions=True):
        self._inlets = inlets or []
        self._outlets = outlets or []
        self._interval = interval
        self._count = -1
        self._job = None
        self._name = name
        self._catch_exceptions = catch_exceptions


    def add_inlets(self, inlets):
        self._inlets.append(inlets)

    @property
    def inlets(self) -> []:
        return self._inlets

    def add_outlets(self, outlet):
        self._outlets.append(outlet)

    @property
    def outlets(self) -> []:
        return self._outlets

    @property
    def interval(self):
        return self._interval

    def set_job(self, job):
        self._job = job

    @property
    def job(self):
        return self._job

    def transfer(self):
        print('asfd')
        self.run()

    def run(self):
        print('asfadf')
        for inlet in self.inlets:
            a = inlet.pull(0)
