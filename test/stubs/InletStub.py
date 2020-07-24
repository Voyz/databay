from databay import Inlet
from databay import Record


class InletStub(Inlet):
    def __init__(self, metadata:dict=None):
        self._metadata = metadata if metadata is not None else {}

    @property
    def metadata(self):
        return self._metadata


    def pull(self, count) -> [Record]:
        return [Record(None, None)]

    def new_record(self, payload, metadata:dict=None):
        full_metadata = {**self._metadata, **(metadata if metadata is not None else {})}
        return Record(payload=payload, metadata=full_metadata)