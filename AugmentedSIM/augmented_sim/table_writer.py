#!/usr/bin/env python3

import csv


class TableWriter:

    def __init__(self, format, columns, file_name):
        self.format = format.upper()
        self.file_name = file_name
        if format == 'CSV':
            self.fd = open(self.file_name, 'w')
            self.writer = csv.DictWriter(
                self.fd,
                columns,
                delimiter=',',
                quoting=csv.QUOTE_NONNUMERIC
            )
        else:
            raise f'Formato “{format}” não suportado.'

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.fd:
            self.fd.close()

    def write_header(self):
        self.writer.writeheader()

    def write_row(self, row):
        self.writer.writerow(row)
