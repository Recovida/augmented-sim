#!/usr/bin/env python3
# coding=utf-8

import csv
import dbfread

from typing import Union, Optional, Iterator, Tuple, Dict

from augmented_sim.i18n import get_translator, get_tr


class TableReadingError(ValueError):

    def __init__(self, message: str, file_name: str,
                 orig_exception: Optional[BaseException] = None):
        super().__init__(message)
        self.message = message
        self.file_name = file_name
        self.orig_exception = orig_exception
        self.details = ''
        if orig_exception:
            import traceback
            tb = traceback.TracebackException.from_exception(orig_exception)
            self.details = ''.join(tb.format())


class TableReader:
    '''Reads a DBF or CSV table.'''

    UNION_ALL_PARSERS = Union[csv.DictReader, dbfread.DBF]

    def __init__(self, file_names: str):
        self.trans = get_translator(None)
        self.tr = get_tr(type(self).__name__, self.trans)
        self.files = []
        self.columns = []
        self.read_count = {}
        self.currently_reading = ''
        self.finished = False
        self.fd = None
        for file_name in file_names:
            self.read_count[file_name] = 0
            try:
                if file_name.lower().endswith('.csv'):
                    format = 'CSV'
                    n, enc = self._count_lines_and_guess_encoding(file_name)
                    denominator = n - 1  # excluding header
                    fd = open(file_name, 'r', encoding=enc)
                    dialect = csv.Sniffer().sniff(fd.read(1024))
                    fd.seek(0)
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
                    msg = self.tr('unsupported-file').format(file_name)
                    raise TableReadingError(msg, file_name)
            except Exception as e:
                msg = self.tr('unsupported-invalid-file').format(file_name)
                raise TableReadingError(msg, file_name, e)
            get_pos = (lambda fn: lambda: self.read_count[fn])(file_name)
            denominator = max(denominator, 1)
            self.files.append(
                [file_name, format, parser, columns, get_pos, 0, denominator]
            )
            for column in columns:
                if column not in self.columns:
                    self.columns.append(column)

    def parse(self) -> Iterator[Dict[str, Union[str, int, float]]]:
        self.finished = False
        for f in self.files:
            file_name, format, parser, columns, get_pos, num, den = f
            self.currently_reading = file_name
            try:
                for row in parser:
                    self.read_count[file_name] += 1
                    f[-2] = min(den, get_pos())
                    yield row
            except Exception as e:
                msg = self.tr('error-reading-file').format(file_name)
                raise TableReadingError(msg, file_name, e)
            f[-1] = get_pos()  # 100% even if denominator fails
        self.currently_reading = ''
        self.finished = True
        if self.fd:
            try:
                self.fd.close()
            except Exception:
                pass
            self.fd = None

    def progress(self) -> Tuple[int, int, int, int, Optional[str]]:
        overall_num = 0
        overall_den = 0
        current = None
        try:
            for f in self.files:
                file_name, format, parser, columns, get_pos, num, den = f
                overall_num += num
                overall_den += den
                if current is None and num < den:
                    current = (num, den)
        except Exception:
            return (0, 1, 0, 1, '')
        else:
            if current is None:
                current = (overall_num and 1, 1)
            return (*current, overall_num, overall_den, self.currently_reading)

    def _count_lines_and_guess_encoding(self, file_name: str) -> \
            Tuple[int, str]:
        encodings = [
            'UTF-8-sig', 'UTF-8', 'UTF-16-BE', 'UTF-16-LE',
            'CP1252', 'ISO-8859-15'
        ]  # the last ones are common in Brazil (on Windows)
        for enc in encodings:
            try:
                with open(file_name, 'r', encoding=enc) as fd:
                    first = fd.readline()
                    if not set(first).intersection(set(',;:- \t')):
                        continue
                    n = 1 + sum(bool(ll.strip()) for ll in fd)
            except UnicodeDecodeError:
                pass
            else:
                return n, enc
        msg = self.tr('unsupported-invalid-file').format(file_name)
        raise TableReadingError(msg, file_name)
