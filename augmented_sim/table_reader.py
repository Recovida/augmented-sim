#!/usr/bin/env python3

import csv
import dbfread

from typing import Union


class TableReader:
    '''Reads a DBF or CSV table.'''

    UNION_ALL_PARSERS = Union[csv.DictReader, dbfread.DBF]

    def __init__(self, file_names: str):
        self.files = []
        self.columns = []
        self.read_count = {}
        self.currently_reading = ''
        self.finished = False
        for file_name in file_names:
            self.read_count[file_name] = 0
            if file_name.lower().endswith('.csv'):
                format = 'CSV'
                fd = open(file_name, 'r', encoding='utf-8-sig')
                dialect = csv.Sniffer().sniff(fd.read(1024))
                fd.seek(0)
                denominator = max(sum(bool(ll.strip()) for ll in fd) - 1, 1)
                fd.seek(0)
                parser = csv.DictReader(fd, dialect=dialect)
                columns = parser.fieldnames
                self.fd = fd
            elif file_name.lower().endswith('.dbf'):
                format = 'DBF'
                parser = dbfread.DBF(file_name)
                columns = parser.field_names[:]
                denominator = parser.header.numrecords
            else:
                raise Exception('Formato não suportado.')
            get_pos = (lambda fn: lambda: self.read_count[fn])(file_name)
            self.files.append(
                [file_name, format, parser, columns, get_pos, 0, denominator]
            )
            for column in columns:
                if column not in self.columns:
                    self.columns.append(column)

    def parse(self):
        self.finished = False
        for f in self.files:
            file_name, format, parser, columns, get_pos, num, den = f
            self.currently_reading = file_name
            for row in parser:
                self.read_count[file_name] += 1
                f[-2] = min(den, get_pos())
                yield row
            f[-1] = get_pos()  # 100% even if denominator fails
        self.currently_reading = ''
        self.finished = True

    def progress(self):
        overall_num = 0
        overall_den = 0
        current = None
        try:
            for f in self.files:
                file_name, format, parser, columns, get_pos, num, den = f
                overall_num += num / den
                overall_den += 1
                if current is None and num < den:
                    current = (num, den)
        except Exception:
            return (0, 1, 0, 1, '')
        else:
            if current is None:
                current = (overall_num and 1, 1)
            return (*current, overall_num, overall_den, self.currently_reading)
