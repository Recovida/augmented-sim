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
    while date < first_epi_week_start:  # this runs at most three times
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
    icd = icd.upper().replace('.', '')[:3]
    if not (len(icd) == 3 and 'A' <= icd[0] <= 'Z' and icd[1:].isnumeric()):
        return invalid
    begin = [
        'A00', 'C00', 'D50', 'E00', 'F00', 'G00', 'H00', 'H60', 'I00', 'J00',
        'K00', 'L00', 'M00', 'N00', 'O00', 'P00', 'Q00', 'R00', 'S00', 'V01',
        'Z00'
    ]
    end = [
        'B99', 'D48', 'D89', 'E90', 'F99', 'G99', 'H59', 'H95', 'I99', 'J99',
        'K93', 'L99', 'M99', 'N99', 'O99', 'P96', 'Q99', 'R99', 'T98', 'Y98',
        'Z99'
    ]
    idx = bisect.bisect(begin, icd)
    if idx <= 0 or icd > end[idx - 1]:
        return invalid
    return idx


def covid(icd):
    invalid, yes, suspected, no = 0, 1, 2, ''
    if icd is None:
        return invalid
    icd = icd.upper().replace('.', '')
    if not (len(icd) >= 3 and 'A' <= icd[0] <= 'Z' and icd[1:].isnumeric()):
        return invalid
    if icd.startswith('B342'):
        return yes
    if icd.startswith('U04'):
        return suspected
    if icd.startswith('U99'):
        return invalid
    return no


CIDBR_LEVELS = {0: {}, 1: {}, 2: {}}
CIDBR_LEVELS[0]['begin'] = [
    'A00', 'A65', 'B25', 'B84', 'C00', 'C15', 'C16', 'C17', 'C18', 'C22',
    'C23', 'C25', 'C26', 'C32', 'C33', 'C37', 'C43', 'C44', 'C50', 'C51',
    'C53', 'C54', 'C56', 'C57', 'C61', 'C62', 'C67', 'C68', 'C70', 'C73',
    'C82', 'C88', 'C90', 'C91', 'C96', 'D00', 'D50', 'D65', 'E00', 'E10',
    'E15', 'E40', 'E50', 'F00', 'F10', 'F20', 'G00', 'G03', 'G04', 'G30',
    'G31', 'G40', 'G43', 'H00', 'H60', 'I00', 'I10', 'I20', 'I26', 'I60',
    'I70', 'I71', 'J00', 'J09', 'J12', 'J20', 'J30', 'J40', 'J60', 'K00',
    'K25', 'K28', 'K65', 'K66', 'K70', 'K80', 'K81', 'K82', 'L00', 'M00',
    'N00', 'N17', 'N20', 'O00', 'O10', 'O11', 'O24', 'O25', 'O26', 'O95',
    'O96', 'O98', 'P00', 'P05', 'P10', 'P20', 'P35', 'Q00', 'Q10', 'Q20',
    'Q30', 'R00', 'R54', 'R55', 'R98', 'R99', 'V01', 'W00', 'W20', 'W65',
    'W75', 'X00', 'X10', 'X40', 'X50', 'X60', 'X85', 'Y10', 'Y35', 'Y40',
]
CIDBR_LEVELS[0]['end'] = [
    'A09', 'A79', 'B49', 'B99', 'C14', 'C15', 'C16', 'C17', 'C21', 'C22',
    'C24', 'C25', 'C31', 'C32', 'C34', 'C41', 'C43', 'C49', 'C50', 'C52',
    'C53', 'C55', 'C56', 'C60', 'C61', 'C66', 'C67', 'C69', 'C72', 'C81',
    'C85', 'C89', 'C90', 'C95', 'C97', 'D48', 'D64', 'D89', 'E07', 'E14',
    'E34', 'E46', 'E90', 'F09', 'F19', 'F99', 'G00', 'G03', 'G25', 'G30',
    'G39', 'G41', 'G98', 'H59', 'H95', 'I09', 'I15', 'I25', 'I52', 'I69',
    'I70', 'I99', 'J06', 'J11', 'J18', 'J22', 'J39', 'J47', 'J99', 'K22',
    'K27', 'K64', 'K65', 'K66', 'K77', 'K80', 'K81', 'K93', 'L99', 'M99',
    'N16', 'N19', 'N99', 'O08', 'O10', 'O23', 'O24', 'O25', 'O92', 'O95',
    'O97', 'O99', 'P04', 'P08', 'P15', 'P29', 'P96', 'Q07', 'Q18', 'Q28',
    'Q99', 'R53', 'R54', 'R96', 'R98', 'R99', 'V99', 'W19', 'W64', 'W74',
    'W99', 'X09', 'X39', 'X49', 'X59', 'X84', 'Y09', 'Y34', 'Y36', 'Y89',
]
CIDBR_LEVELS[0]['values'] = [
    '001', '031', '031', '031', '032', '033', '034', '052', '035', '036',
    '052', '037', '052', '038', '039', '052', '040', '052', '041', '052',
    '042', '043', '044', '052', '045', '052', '046', '052', '047', '052',
    '048', '052', '049', '050', '052', '051', '053', '054', '057', '055',
    '057', '056', '057', '059', '058', '059', '060', '060', '063', '061',
    '063', '062', '063', '064', '065', '066', '067', '068', '069', '070',
    '071', '072', '077', '073', '074', '075', '077', '076', '077', '082',
    '078', '082', '079', '082', '080', '082', '081', '082', '083', '084',
    '085', '086', '087', '088', '090', '089', '090', '090', '089', '091',
    '092', '090', '093', '094', '095', '096', '097', '098', '100', '099',
    '100', '103', '101', '103', '102', '103', '104', '105', '113', '106',
    '113', '107', '113', '108', '113', '109', '110', '111', '112', '113',
]
CIDBR_LEVELS[1]['begin'] = [
    'A00', 'A01', 'A09', 'A15', 'A17', 'A20', 'A27', 'A30', 'A33', 'A36',
    'A37', 'A39', 'A40', 'A50', 'A80', 'A82', 'A90', 'A91', 'A95', 'A96',
    'B05', 'B15', 'B20', 'B50', 'B55', 'B57', 'B58', 'B65', 'B66', 'B69',
    'B70', 'F10', 'I21', 'J21', 'J45', 'K70', 'K71', 'K74', 'K75',
]
CIDBR_LEVELS[1]['end'] = [
    'A00', 'A08', 'A09', 'A16', 'A19', 'A20', 'A27', 'A30', 'A35', 'A36',
    'A37', 'A39', 'A41', 'A64', 'A80', 'A82', 'A90', 'A94', 'A95', 'A99',
    'B05', 'B19', 'B24', 'B54', 'B55', 'B57', 'B58', 'B65', 'B68', 'B69',
    'B83', 'F10', 'I21', 'J21', 'J46', 'K70', 'K73', 'K74', 'K77',
]
CIDBR_LEVELS[1]['values'] = [
    '002', '004', '003', '005', '006', '007', '008', '009', '010', '011',
    '012', '013', '014', '015', '016', '017', '018', '020', '019', '020',
    '021', '022', '023', '024', '025', '026', '027', '028', '030', '029',
    '030', '058.1', '068.1', '075.1', '076.1', '080.1', '080.3', '080.2',
    '080.3',
]
CIDBR_LEVELS[2]['begin'] = [
    'A01', 'A33', 'A34', 'A35',
]
CIDBR_LEVELS[2]['end'] = [
    'A01', 'A33', 'A34', 'A35',
]
CIDBR_LEVELS[2]['values'] = [
    '004.1', '010.1', '010.2', '010.3',
]


def icd_to_cidbr(icd):
    invalid = ''
    if icd is None:
        return invalid
    icd = icd.upper().replace('.', '')
    if not (len(icd) >= 3 and 'A' <= icd[0] <= 'Z' and icd[1:].isnumeric()):
        return invalid
    if icd.startswith('O244'):  # special case
        return '089'
    for level in [2, 1, 0]:
        idx = bisect.bisect(CIDBR_LEVELS[level]['begin'], icd[:3])
        if idx > 0 and icd[:3] <= CIDBR_LEVELS[level]['end'][idx - 1]:
            return CIDBR_LEVELS[level]['values'][idx - 1]
    return invalid


def cidbr_short_label(cidbr):
    if not cidbr:
        return ''
    cidbr_int = int(cidbr[:3])
    if 88 <= cidbr_int <= 92:
        return cidbr + ' GPP' + str(cidbr_int - 87)
    if 93 <= cidbr_int <= 97:
        return cidbr + ' PERI' + str(cidbr_int - 92)
    named = {
        '068': 'DCOR',
        '069': 'OUTCOR',
        '070': 'AVC',
        '073': 'GRIPE',
        '074': 'PNEUMONIA',
        '075': 'PNEUMONIA',
        '076': 'DPOCASMA',
        '104': 'ACTRANS',
        '105': 'QUEDAFOGINT',
        '106': 'QUEDAFOGINT',
        '107': 'QUEDAFOGINT',
        '108': 'QUEDAFOGINT',
        '109': 'SUIC',
        '110': 'HOMIC',
        '111': 'EXTIND',
        '112': 'INTLEG',
        '113': 'OUTEXT',
    }
    for pfx, name in named.items():
        if cidbr.startswith(pfx):
            return name
    return ''


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
        #  'DISTRITOSAUDE',  # ?
        #  'CAUSAESP',       # ?
    ] + cols[1:2] + [
        'IDADEGERAL',     # age in years (0 if < 1 year old)
        'IDADECAT1',      # ?
        'IDADECAT2'       # age category (1..8)
    ] + cols[2:5] + [
        'AREARENDA',      # neighbourhood income (ALTA/INTERMEDIARIA/BAIXA)
    ] + cols[5:] + [
        'CAPCID',         # ICD chapter (integer)
        'COVID',          # 0=unknown, 1=yes, 2=suspected
        'CIDBR',          # CID-BR code (usually an integer)
        'CIDBRDESC',      # CID-BR short name (only for a few cases)
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
            cidbr = icd_to_cidbr(row['CAUSABAS'])
            row['CIDBR'] = cidbr
            row['CIDBRDESC'] = cidbr_short_label(cidbr)

            # finally, write to the CSV file
            writer.writerow(row)


if __name__ == '__main__':
    main()
