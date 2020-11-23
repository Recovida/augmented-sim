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


FIRST_EPIDEMIOLOGICAL_WEEK_CACHE = {}


def first_epi_week_start_in_year(year):
    if year in FIRST_EPIDEMIOLOGICAL_WEEK_CACHE:
        return FIRST_EPIDEMIOLOGICAL_WEEK_CACHE[year]
    first_day_in_year = datetime.date(year, 1, 1)
    weekday = first_day_in_year.weekday()
    first_sunday_in_year = datetime.date(year, 1, 7 - weekday)
    if weekday >= 3:  # Thu, Fri, Sat or Sun
        start = first_sunday_in_year
    else:
        start = first_sunday_in_year - datetime.timedelta(days=7)
    FIRST_EPIDEMIOLOGICAL_WEEK_CACHE[year] = start
    return start


def epidemiological_week(date):
    year = date.year + 1
    first_epi_week_start = first_epi_week_start_in_year(year)
    while date < first_epi_week_start:  # this runs at most twice
        year -= 1
        first_epi_week_start = first_epi_week_start_in_year(year)
    return (year, 1 + ((date - first_epi_week_start).days) // 7)



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
        'DIA',            # 1..31
        'MES',            # 1..12
        'ANO',            # YYYY
        'ANOEPI',         # year of the epidemiological week
        'SEMANAEPI',      # epidemiological week (1..53)
        'AREARENDA',      # ?
        'DISTRITOSAUDE',  # ?
        'CAPCID',         # ?
        'CAUSAESP',       # ?
    ] + cols[1:2] + ['IDADEANOS'] + cols[2:]
    with open(a.output_file.name, 'w') as fd:
        writer = csv.DictWriter(fd, cols, delimiter=',',
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for row in all_rows:
            # parse date and add columns with the extracted data
            date = parse_date(row['DTOBITO'])
            epi_year, epi_week = epidemiological_week(date)
            row.update({
                'DIA': date.day,
                'MES': date.month,
                'ANO': date.year,
                'ANOEPI': epi_year,
                'SEMANAEPI': epi_week,
            })
            # parse age and add columns with the extracted data
            age = parse_age(row['IDADE'])
            if age is not None:
                row['IDADEANOS'] = age.years
            # finally, write to the CSV file
            writer.writerow(row)


if __name__ == '__main__':
    main()
