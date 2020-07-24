
class MissingLinkError(RuntimeError):
    """ Raised when providing a link that isn't stored in planner."""
    pass


class ImplementationError(RuntimeError):
    """ Raised when concrete implementation is incorrect."""
    pass

class InvalidNodeError(RuntimeError):
    """ Raised when invalid node (inlet or outlet) is provided."""
    pass