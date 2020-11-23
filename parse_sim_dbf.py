#!/usr/bin/env python3

import argparse
import csv
import dbfread
import datetime

from dateutil.relativedelta import relativedelta


def parse_date(d):
    try:
        year = int(d[4:])
        month = int(d[2:4])
        day = int(d[:2])
    except (TypeError, ValueError):
        return None
    return datetime.date(year, month, day)


def parse_age(d):
    try:
        unit, value = int(d[:1]), int(d[1:])
    except (TypeError, ValueError):
        return None
    if unit == 5:
        unit, value = 4, value + 100
    args = ['minutes', 'hours', 'days', 'months', 'years']
    if 0 <= unit < len(args):
        return relativedelta(**{args[unit]: value})
    return None


def main():
    desc = '''
    This script reads a DBF file containing death causes encoded
    according to "Sistema de Informação sobre Mortalidade" (SIM).
    It adds a few columns and saves the file as CSV.
    '''
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('input_file', type=argparse.FileType('r'),
                        help='input file name (DBF)')
    parser.add_argument('output_file', type=argparse.FileType('w'),
                        help='output file name (CSV)')
    a = parser.parse_args()
    with dbfread.DBF(a.input_file.name) as reader:
        all_rows = [row for row in reader]
        cols = reader.field_names
    cols = cols[:1] + [
        'DATA',           # 1..31
        'SEMANAEPI',      # ?
        'MES',            # 1..12
        'ANO',            # YYYY
        'AREARENDA',      # ?
        'DISTRITOSAUDE',  # ?
        'CAPCID',         # ?
        'CAUSAESP',       # ?
    ] + cols[1:]
    with open(a.output_file.name, 'w') as fd:
        writer = csv.DictWriter(fd, cols, delimiter=',',
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in all_rows:
            # parse date and add columns with the extracted data
            date = parse_date(row['DTOBITO'])
            row.update({
                'DATA': date.day,
                'ANO': date.month,
                'MES': date.year,
            })
            writer.writerow(row)


if __name__ == '__main__':
    main()
