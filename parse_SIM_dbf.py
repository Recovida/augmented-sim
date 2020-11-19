#!/usr/bin/env python3

import argparse
import dbfread
import datetime
import sys

from dateutil.relativedelta import relativedelta



class SIMFieldParser(dbfread.FieldParser):

    def parseC(self, field, data):
        if field.name.startswith('DT') and field.length == 8:
            try:
                year = int(data[4:])
                month = int(data[2:4])
                day = int(data[:2])
            except:
                return dbfread.InvalidValue(data)
            return datetime.date(year, month, day)
        if field.name == 'IDADE' and field.length == 3:
            try:
                unit, value = int(data[:1]), int(data[1:])
            except:
                return dbfread.InvalidValue(data)
            if unit == 5:
                unit, value = 4, value + 100
            args = ['minutes', 'hours', 'days', 'months', 'years']
            if 0 <= unit < len(args):
                return relativedelta(**{args[unit]: value})
            return dbfread.InvalidValue(data)
        return super().parseC(field, data)


class SIMCauseEntry:

    def __init__(self):
        pass

    @classmethod
    def from_dbf_row(cls, linha):
        return None





def main():
    desc = 'This script reads a DBF file containing death causes encoded '  \
            'according to "Sistema de Informação sobre Mortalidade" (SIM)'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('files', nargs='+', type=argparse.FileType('r'),
                        help='DBF file names')
    a = parser.parse_args()
    n = 0
    for f in a.files:
        print('Reading', f.name)
        with dbfread.DBF(f.name, parserclass=SIMFieldParser) as dbf:
            for row in dbf:
                n += 1
                print(row)
                if n >= 20:
                    break

if __name__ == '__main__':
    main()
