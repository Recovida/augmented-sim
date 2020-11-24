#!/usr/bin/env python3

import argparse
import csv
import dbfread
import datetime
import re

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


NEIGHBOURHOOD_INCOME_STR = '''
(11=3) (12=1) (13=3) (17=3) (18=2) (19=3) (28=3) (29=2) (33=1) (34=1) (36=3)
(37=2) (38=3) (44=1) (45=3) (46=2) (47=3) (50=2) (51=1) (52=3) (56=3) (57=2)
(60=2) (61=1) (62=3) (63=1) (67=1) (79=1) (80=2) (83=3) (84=1) (85=2) (86=3)
(89=3) (90=1) (91=2) (92=1) (96=1) (1thru2=1) (3thru5=2) (6thru8=1)
(9thru10=2) (14thru16=1) (20thru21=2) (22thru25=3) (26thru27=1)
(30thru32=3) (39thru40=2) (41thru43=3) (48thru49=1) (53thru55=1)
(58thru59=3) (64thru66=2) (68thru69=2) (70thru72=1) (73thru74=2)
(74thru78=3) (81thru82=1) (87thru88=2) (93thru95=2)
'''
NEIGHBOURHOOD_INCOME_TABLE = {}
INCOME_VALUES = {1: 'ALTA', 2: 'INTERMEDIARIA', 3: 'BAIXA'}


def fill_neighbourhood_income():
    single_pattern = re.compile(r'\((?P<n>\d+)=(?P<inc>\d)\)')
    range_pattern = re.compile(r'\((?P<n1>\d+)thru(?P<n2>\d+)=(?P<inc>\d)\)')
    for item in NEIGHBOURHOOD_INCOME_STR.strip().replace('\n', ' ').split(' '):
        if (m := single_pattern.match(item)):
            n = int(m.group('n'))
            inc = INCOME_VALUES.get(int(m.group('inc')), '')
            NEIGHBOURHOOD_INCOME_TABLE[n] = inc
        elif (m := range_pattern.match(item)):
            inc = INCOME_VALUES.get(int(m.group('inc')), '')
            n1 = n = int(m.group('n1'))
            n2 = n = int(m.group('n2'))
            for n in range(n1, n2 + 1):
                NEIGHBOURHOOD_INCOME_TABLE[n] = inc


fill_neighbourhood_income()


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
        'DIA',            # day of the month (1..31)
        'MES',            # month (1..12)
        'ANO',            # year (YYYY)
        'ANOEPI',         # year of the epidemiological week (YYYY)
        'SEMANAEPI',      # epidemiological week (1..53)
        'AREARENDA',      # neighbourhood income (ALTA/INTERMEDIARIA/BAIXA)
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
            # add neighbourhood income column
            if row['CODBAIRES']:
                neighbourhood = int(row['CODBAIRES'])
                income = NEIGHBOURHOOD_INCOME_TABLE.get(neighbourhood, '')
                row['AREARENDA'] = income
            # finally, write to the CSV file
            writer.writerow(row)


if __name__ == '__main__':
    main()
