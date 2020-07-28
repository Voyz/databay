import random

from databay import Inlet


class RandomIntInlet(Inlet):

    def __init__(self, min:int=0, max:int=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min = min
        self.max = max

    def pull(self, update):
        return random.randint(self.min, self.max)