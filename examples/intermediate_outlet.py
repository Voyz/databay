from datetime import timedelta

from databay import Link
from databay.inlets import RandomIntInlet
from databay.planners import APSPlanner
from databay.record import Record
from databay.outlet import Outlet

class FileOutlet(Outlet):

    FILEPATH = 'FileOutlet.FILEPATH'
    """Filepath of the file to write to."""

    FILE_MODE = 'FileOutlet.FILE_MODE'
    """Write mode to use when writing into the csv file."""

    def __init__(self,
                 default_filepath:str='outputs/default_output.txt',
                 default_file_mode:str='a'):

        super().__init__()

        self.default_filepath = default_filepath
        self.default_file_mode = default_file_mode

    def push(self, records:[Record], update):
        for record in records:
            filepath = record.metadata.get(self.FILEPATH, self.default_filepath)
            file_mode = record.metadata.get(self.FILE_MODE, self.default_file_mode)

            with open(filepath, file_mode) as f:
                f.write(str(record.payload)+'\n')


metadata = {
    FileOutlet.FILEPATH: 'outputs/random_ints.txt',
    FileOutlet.FILE_MODE: 'a'
}
random_int_inlet = RandomIntInlet(metadata=metadata)
file_outlet = FileOutlet()

link = Link(random_int_inlet,
            file_outlet,
            interval=timedelta(seconds=2),
            name='file_outlet')

planner = APSPlanner(link)
planner.start()