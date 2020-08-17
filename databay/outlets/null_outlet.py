from databay.outlet import Outlet
from databay.record import Record


class NullOutlet(Outlet): # pragma: no cover
    """
    Outlet that doesn't do anything, essentially a 'no-op' outlet.
    """

    async def push(self, records:[Record], update):
        """
        Doesn't do anything.
        """
        pass