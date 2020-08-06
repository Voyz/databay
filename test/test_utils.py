

def fqname(obj):
    return ".".join([obj.__module__, obj.__name__])

class DummyException(Exception):
    """ Raised when they add coriander to all your food."""

    def __init__(self, message="I'm a dummy exception"):
        self.message = message
        super().__init__(self.message)

class DummyUnusualException(Exception):
    """ Raised when they add parsley to all your food."""

    def __init__(self, argA:int, argB:bool):
        super().__init__(f'{argA}, {argB}, I\'m an unusual dummy exception')