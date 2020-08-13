from databay import Inlet

class NullInlet(Inlet): # pragma: no cover
    """
    Inlet that doesn't do anything, essentially a 'no-op' inlet.
    """

    def pull(self, update):
        """
        Doesn't produce anything.

        :returns: empty list
        """
        return []