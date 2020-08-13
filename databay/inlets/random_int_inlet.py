import random

from databay import Inlet


class RandomIntInlet(Inlet): # pragma: no cover
    """
    Inlet that will generate a random integer within the specified range.
    """

    def __init__(self, min:int=0, max:int=100, *args, **kwargs):
        """

        :param min: Lower boundary of the random range.
        :type min: int
        :param max: Upper boundary of the random range.
        :type max: int
        """

        super().__init__(*args, **kwargs)
        self.min = min
        self.max = max

    def pull(self, update):
        """
        Produces a random integer within the specified range.

        :type update: :any:`Update`
        :param update: Update object representing the particular Link update run.

        :return: Single or multiple records produced.
        :rtype: :any:`Record` or list[:any:`Record`]
        """
        return random.randint(self.min, self.max)