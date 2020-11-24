#!/usr/bin/env python3

import argparse
import bisect
import csv
import dbfread
import datetime

from dateutil.relativedelta import relativedelta


# --------- Date

def parse_date(d):
    try:
        year = int(d[4:])
        month = int(d[2:4])
        day = int(d[:2])
    except (TypeError, ValueError):
        return None
    return datetime.date(year, month, day)


# --------- Age

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


def age_category1(age):
    return 0


def age_category2(age):
    return bisect.bisect([0, 5, 20, 40, 60, 70, 80, 90], age)


# --------- Epidemiological week

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


# --------- Neighbourhood income

neighbourhood_income_table = {
    1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 1, 7: 1, 8: 1, 9: 2,
    10: 2, 11: 3, 12: 1, 13: 3, 14: 1, 15: 1, 16: 1, 17: 3, 18: 2, 19: 3,
    20: 2, 21: 2, 22: 3, 23: 3, 24: 3, 25: 3, 26: 1, 27: 1, 28: 3, 29: 2,
    30: 3, 31: 3, 32: 3, 33: 1, 34: 1, 36: 3, 37: 2, 38: 3, 39: 2,
    40: 2, 41: 3, 42: 3, 43: 3, 44: 1, 45: 3, 46: 2, 47: 3, 48: 1, 49: 1,
    50: 2, 51: 1, 52: 3, 53: 1, 54: 1, 55: 1, 56: 3, 57: 2, 58: 3, 59: 3,
    60: 2, 61: 1, 62: 3, 63: 1, 64: 2, 65: 2, 66: 2, 67: 1, 68: 2, 69: 2,
    70: 1, 71: 1, 72: 1, 73: 2, 74: 3, 75: 3, 76: 3, 77: 3, 78: 3, 79: 1,
    80: 2, 81: 1, 82: 1, 83: 3, 84: 1, 85: 2, 86: 3, 87: 2, 88: 2, 89: 3,
    90: 1, 91: 2, 92: 1, 93: 2, 94: 2, 95: 2, 96: 1
}
neighbourhood_income_names = {1: 'ALTA', 2: 'INTERMEDIARIA', 3: 'BAIXA'}


def neighbourhood_income(neighbourhood):
    try:
        neighbourhood = int(neighbourhood)
    except (TypeError, ValueError):
        return ''
    income_id = neighbourhood_income_table.get(neighbourhood, -1)
    return neighbourhood_income_names.get(income_id, '')


# --------- ICD

def icd_chapter(icd):
    invalid = '**'
    if icd is None:
        return invalid
    icd = icd.upper()[:3]
    if not (len(icd) == 3 and 'A' <= icd[0] <= 'Z' and icd[1:].isnumeric()):
        return invalid
    beg = ['A00', 'C00', 'D50', 'E00', 'F00', 'G00', 'H00', 'H60', 'I00',
           'J00', 'K00', 'L00', 'M00', 'N00', 'O00', 'P00', 'Q00', 'R00',
           'S00', 'V01', 'Z00']
    end = ['B99', 'D48', 'D89', 'E90', 'F99', 'G99', 'H59', 'H95', 'I99',
           'J99', 'K93', 'L99', 'M99', 'N99', 'O99', 'P96', 'Q99', 'R99',
           'T98', 'Y98', 'Z99']
    idx = bisect.bisect(beg, icd)
    if idx <= 0 or icd > end[idx - 1]:
        return invalid
    return idx


def covid(icd):
    invalid, yes, suspected, no = 0, 1, 2, ''
    if icd is None:
        return invalid
    icd = icd.upper()
    if not (len(icd) >= 3 and 'A' <= icd[0] <= 'Z' and icd[1:].isnumeric()):
        return invalid
    if icd.startswith('B342'):
        return yes
    if icd.startswith('U04'):
        return suspected
    return no


# --------- main function

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
        'CAUSAESP',       # ?
    ] + cols[1:2] + [
        'IDADEGERAL',     # age in years (0 if < 1 year old)
        'IDADECAT1',      # ?
        'IDADECAT2'       # age category (1..8)
    ] + cols[2:] + [
        'CAPCID',         # ICD chapter (integer)
        'COVID',          # 0=unknown, 1=yes, 2=suspected
        'CIDBR',          # ?
    ]
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
                row['IDADEGERAL'] = age.years
                row['IDADECAT1'] = age_category1(age.years)
                row['IDADECAT2'] = age_category2(age.years)

            # add neighbourhood income column
            row['AREARENDA'] = neighbourhood_income(row['CODBAIRES'])

            # data obtained from ICD column
            row['CAPCID'] = icd_chapter(row['CAUSABAS'])
            row['COVID'] = covid(row['CAUSABAS'])

            # finally, write to the CSV file
            writer.writerow(row)


if __name__ == '__main__':
    main()
