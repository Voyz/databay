from enum import Enum

from databay import Inlet


class FileInletMode(Enum):
    """Enum defining the mode in which the FileInlet should read the file."""

    LINE: str = 'line'
    """Read file one line per transfer. This will open the file and hold it open for as long as the planner is running."""

    FILE: str = 'file'
    """Read the entire file on each transfer. This will only open the file briefly during the transfer."""


class FileInlet(Inlet):

    """
    Inlet producing data by reading a file.
    """

    def __init__(self, filepath: str, read_mode: FileInletMode = FileInletMode.LINE, *args, **kwargs):
        """
        :param filepath: Path to the file.
        :type filepath: str

        :param read_mode: Mode in which the file is to be read.
        :type read_mode: :any:`FileInletMode`
        """
        super().__init__(*args, **kwargs)
        self.filepath = filepath
        self.read_mode = read_mode

    def pull(self, update):
        """
        Produce data by reading a file in the mode specified.

        :raises: :any:`FileNotFoundError` if file does not exists.
        :returns: contents of the file.
        """

        # todo: more file parsing options, decoding, etc.

        if self.read_mode is FileInletMode.FILE:
            with open(self.filepath, 'r') as f:
                return f.read()

        elif self.read_mode is FileInletMode.LINE:
            return self.file.readline()

    def on_start(self):
        """
        If read mode is :any:`FileInletMode.LINE`, open the file and hold it open for reading.

        :raises: :any:`FileNotFoundError` if file does not exists.
         """
        if self.read_mode is FileInletMode.LINE:
            self.file = open(self.filepath, 'r')

    def on_shutdown(self):
        """ If read mode is :any:`FileInletMode.LINE`, close the file."""
        if self.read_mode is FileInletMode.LINE:
            self.file.close()

    def __repr__(self):
        s = "%s(" % (self.__class__.__name__)

        s += f'filepath={self.filepath}'
        s += f', read_mode={self.read_mode}'

        if self.metadata:
            s += ', metadata=%s' % self.metadata

        s += ')'

        return s
