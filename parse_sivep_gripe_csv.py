#!/usr/bin/env python3

import argparse
import csv
import datetime
import re

# from dateutil.relativedelta import relativedelta

DATE_PATTERNS = [
    re.compile(r'(?P<d>\d?\d)/(?P<m>\d?\d)/(?P<y>\d{4})'),
    re.compile(r'(?P<y>\d{4})-(?P<m>\d?\d)-(?P<d>\d?\d)'),
]


def process_row(row):
    for k in row:
        value = row[k]
        if k.startswith('Dt ') and isinstance(value, str):
            for p in DATE_PATTERNS:
                if (match := p.match(value)):
                    year = int(match.group('y'))
                    month = int(match.group('m'))
                    day = int(match.group('d'))
                    row[k] = datetime.date(year, month, day)


def main():
    desc = 'This script reads a CSV file containing death causes encoded '  \
            'according to "SISTEMA DE INFORMAÇÃO DE VIGILÂNCIA ' \
            'EPIDEMIOLÓGICA DA GRIPE" (SIVEP-Gripe)'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('files', nargs='+', type=argparse.FileType('r'),
                        help='DBF file names')
    a = parser.parse_args()
    n = 0
    for f in a.files:
        print('Reading', f.name)
        with open(f.name, 'r', encoding='utf-8-sig') as fd:
            dialect = csv.Sniffer().sniff(fd.read(1024))
            fd.seek(0)
            reader = csv.DictReader(fd, dialect=dialect)
            for row in reader:
                n += 1
                process_row(row)
                print('\n' + 70 * '-' + '\n' + 'Linha', n)
                for k, v in row.items():
                    print('%20s = %s' % (k, v))
                input('[Press ENTER to continue]')


if __name__ == '__main__':
    main()
