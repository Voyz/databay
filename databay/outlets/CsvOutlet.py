import csv

from databay.outlet import Outlet
from databay.record import Record


class CsvOutlet(Outlet):

    def __init__(self, csv_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_file = csv_file

    async def push(self, records:[Record], update):
        for record in records:
            print(update, 'writing', record)
            csv_file = self.csv_file
            if 'csv_file' in record.metadata:
                csv_file = record.metadata['csv_file']

            with open(csv_file, 'a') as f:
                writer = csv.DictWriter(f, record.payload.keys())
                writer.writerow(record.payload)
