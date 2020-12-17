
class Record():
    """
    Data structure representing the data passed between inlets and outlets.

    .. warning:: You should prefer :py:func:`Inlet.new_record() <databay.inlet.Inlet.new_record>` function over instantiating this class directly.
    """

    def __init__(self, payload, metadata: dict = None):
        """

        :type payload: Any
        :param payload: Data contained by this record.

        :type metadata: dict
        :param metadata: Metadata attached to this record |default| :code:`None` (Set to empty :code:`dict` if not provided)
        """

        self._payload = payload
        self._metadata = metadata if metadata is not None else {}

    @property
    def payload(self) -> dict:
        """
        :returns: Data stored in this record.
        :rtype: Any
        """

        return self._payload

    @property
    def metadata(self) -> dict:
        """
        :returns: Metadata attached to this record.
        :rtype: :any:`dict`
        """

        return self._metadata

    def __repr__(self):
        """
        :returns: Record(payload=%s, metadata=%s)
        """

        return ('Record(payload=%s, metadata=%s)' % (self.payload, self.metadata))
