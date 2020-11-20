#!/usr/bin/env python3

import argparse
import dbfread
import datetime

from dateutil.relativedelta import relativedelta


class SIMFieldParser(dbfread.FieldParser):

    def parseC(self, field, data):
        if field.name.startswith('DT') and field.length == 8:
            try:
                year = int(data[4:])
                month = int(data[2:4])
                day = int(data[:2])
            except (TypeError, ValueError):
                return dbfread.InvalidValue(data)
            return datetime.date(year, month, day)
        if field.name == 'IDADE' and field.length == 3:
            try:
                unit, value = int(data[:1]), int(data[1:])
            except (TypeError, ValueError):
                return dbfread.InvalidValue(data)
            if unit == 5:
                unit, value = 4, value + 100
            args = ['minutes', 'hours', 'days', 'months', 'years']
            if 0 <= unit < len(args):
                return relativedelta(**{args[unit]: value})
            return dbfread.InvalidValue(data)
        return super().parseC(field, data)


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
                print('\n' + 70 * '-' + '\n' + 'Linha', n)
                for k, v in row.items():
                    print('%20s = %s' % (k, v))
                input('[Press ENTER to continue]')


if __name__ == '__main__':
    main()
