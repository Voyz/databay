

def fqname(obj):
    return ".".join([obj.__module__, obj.__name__])

class DummyException(Exception):
    """ Raised when they add coriander to all your food."""

    def __init__(self, message="I'm a dummy exception"):
        self.message = message
        super().__init__(self.message)