from databay.inlets.file_inlet import FileInlet, FileInletMode
from databay.misc import inlet_tester


class TestFileInlet(inlet_tester.InletTester):

    def get_inlet(self):
        return [
            FileInlet(__file__),
            FileInlet(__file__, read_mode=FileInletMode.FILE),
        ]
