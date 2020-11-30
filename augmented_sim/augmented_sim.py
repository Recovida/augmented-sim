#!/usr/bin/env python3

import argparse
import bisect
import csv
import dbfread
import datetime

from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple, Union, Dict


class TableParser:
    '''Reads a DBF or CSV table.'''

    def __init__(self, file_name: str):
        self.file_name = file_name
        if file_name.lower().endswith('.csv'):
            self.format = 'CSV'
            self.fd = open(file_name, 'r', encoding='utf-8-sig')
            dialect = csv.Sniffer().sniff(self.fd.read(1024))
            self.fd.seek(0)
            self.parser = csv.DictReader(self.fd, dialect=dialect)
            self.columns = self.parser.fieldnames[:]
        elif file_name.lower().endswith('.dbf'):
            self.format = 'DBF'
            self.parser = dbfread.DBF(file_name)
            self.columns = self.parser.field_names[:]
        else:
            raise Exception('Formato não suportado.')

    def parse(self):
        if self.format == 'CSV':
            for row in self.parser:
                yield row
            self.fd.close()
        elif self.format == 'DBF':
            for row in self.parser:
                yield row


class SIMRowParser:
    '''Parses a row of SIM values, converting them to appropriate types.'''

    @classmethod
    def parse_date(cls, d: str) -> Optional[datetime.date]:
        # foreseeing a problem caused by spreadsheets:
        if isinstance(d, str) and len(d) == 7:
            d = '0' + d
        try:
            return datetime.datetime.strptime(d, '%d%m%Y').date()
        except (TypeError, ValueError):
            return None

    @classmethod
    def parse_age(cls, d: str) -> Optional[relativedelta]:
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

    @classmethod
    def parse_icd(cls, icd: str) -> Optional[str]:
        if not icd:
            return None
        icd = icd.upper().replace('.', '')
        if not (len(icd) >= 3 and 'A' <= icd[0] <= 'Z'):
            return None
        return icd

    @classmethod
    def parse_int(cls, value: str) -> Optional[int]:
        try:
            return int(str)
        except Exception:
            return None

    @classmethod
    def parse_row(cls, row):
        converters = {
            'DTOBITO': cls.parse_date,
            'IDADE': cls.parse_age,
            'CODBAIRES': cls.parse_int,
            'CAUSABAS': cls.parse_icd
        }
        return {k: converters.get(k, lambda x: x)(v) for k, v in row.items()}


class Augmenter:
    '''Produces extra columns on a SIM table.'''

    REQUIRES = []
    PRODUCES = []

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        pass


class DeathDateAugmenter(Augmenter):

    REQUIRES = ['DTOBITO']
    PRODUCES = [
        'DIA',            # day of the month (1..31)
        'MES',            # month (1..12)
        'ANO',            # year (YYYY)
        'ANOEPI',         # year of the epidemiological week (YYYY)
        'SEMANAEPI',      # epidemiological week (1..53)
    ]

    FIRST_EPIDEMIOLOGICAL_WEEK_CACHE = {}

    @classmethod
    def first_epi_week_start_in_year(cls, year: int) -> datetime.date:
        if year in cls.FIRST_EPIDEMIOLOGICAL_WEEK_CACHE:
            return cls.FIRST_EPIDEMIOLOGICAL_WEEK_CACHE[year]
        first_day_in_year = datetime.date(year, 1, 1)
        weekday = first_day_in_year.weekday()
        first_sunday_in_year = datetime.date(year, 1, 7 - weekday)
        if weekday >= 3:  # Thu, Fri, Sat or Sun
            start = first_sunday_in_year
        else:
            start = first_sunday_in_year - datetime.timedelta(days=7)
        cls.FIRST_EPIDEMIOLOGICAL_WEEK_CACHE[year] = start
        return start

    @classmethod
    def epidemiological_week(cls, date: datetime.date) -> Tuple[int, int]:
        year = date.year + 1
        first_epi_week_start = cls.first_epi_week_start_in_year(year)
        while date < first_epi_week_start:  # this runs at most three times
            year -= 1
            first_epi_week_start = cls.first_epi_week_start_in_year(year)
        return (year, 1 + ((date - first_epi_week_start).days) // 7)

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        d = row.get('DTOBITO', None)
        if not d:
            return {}
        epi_year, epi_week = cls.epidemiological_week(d)
        return {
            'DIA': d.day,
            'MES': d.month,
            'ANO': d.year,
            'ANOEPI': d.year,
            'SEMANAEPI': d.year,
        }


class AgeAugmenter(Augmenter):

    REQUIRES = ['IDADE']
    PRODUCES = [
        'IDADEGERAL',     # age in years (0 if < 1 year old)
        'IDADECAT1',      # ?
        'IDADECAT2'       # age category (1..8)
    ]

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        age = row.get('IDADE', None)
        if age is None:
            return {}
        return {
            'IDADEGERAL':
                age.years,
            'IDADECAT1':
                0,
            'IDADECAT2':
                bisect.bisect([0, 5, 20, 40, 60, 70, 80, 90], age.years)
        }


class NeighbourhoodAugmenter(Augmenter):

    REQUIRES = ['CODBAIRES']
    PRODUCES = [
        'AREARENDA',      # neighbourhood income (ALTA/INTERMEDIARIA/BAIXA)
    ]

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

    @classmethod
    def neighbourhood_income(cls, neighbourhood: int) -> str:
        income_id = cls.neighbourhood_income_table.get(neighbourhood, -1)
        return cls.neighbourhood_income_names.get(income_id, None)

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        neighbourhood = row.get('CODBAIRES', None)
        if neighbourhood is None:
            return {}
        income = cls.neighbourhood_income(neighbourhood)
        return {
            'AREARENDA': income
        } if income else {}


class DeathCauseAugmenter(Augmenter):

    REQUIRES = ['CAUSABAS']
    PRODUCES = [
        'CAPCID',       # ICD chapter (integer)
        'COVID',        # 0=unknown, 1=yes, 2=suspected
        'CIDBR',        # CID-BR code (usually an integer)
        'DCOR',         # heart diseases (0/1)
        'OUTCOR',       # other heart diseases (0/1)
        'AVC',          # CVA [stroke] (0/1)
        'GRIPE',        # flu (0/1)
        'PNEUMONIA',    # pneumonia (0/1)
        'DPOCASMA',     # COPD or asthma (0/1)
        'GPP',          # pregnancy, childbirth and the puerperium (0..5)
        'PERI',         # perinatal conditions (0..5)
        'ACTRANS',      # transport accidents (0/1)
        'QUEDAFOGINT',  # fall, drowning or poisoning (0/1)
        'SUIC',         # suicide (0/1)
        'HOMIC',        # homicide (0/1)
        'EXTIND',       # event of undetermined intent (0/1)
        'INTLEG',       # legal intervention and operations of war (0/1)
        'OUTEXT'        # other external causes (0/1)
    ]

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

    ICD_CHAPTER_BEGIN = [
        'A00', 'C00', 'D50', 'E00', 'F00', 'G00', 'H00', 'H60', 'I00', 'J00',
        'K00', 'L00', 'M00', 'N00', 'O00', 'P00', 'Q00', 'R00', 'S00', 'V01',
        'Z00'
    ]
    ICD_CHAPTER_END = [
        'B99', 'D48', 'D89', 'E90', 'F99', 'G99', 'H59', 'H95', 'I99', 'J99',
        'K93', 'L99', 'M99', 'N99', 'O99', 'P96', 'Q99', 'R99', 'T98', 'Y98',
        'Z99'
    ]

    INVALID_ICD_CHAPTER = '**'
    INVALID_COVID = 0

    @classmethod
    def icd_chapter(cls, icd: str) -> Union[str, int]:
        icd = icd.upper().replace('.', '')[:3]
        if len(icd) == 3 and 'A' <= icd[0] <= 'Z' and icd[1:].isnumeric():
            idx = bisect.bisect(cls.ICD_CHAPTER_BEGIN, icd)
            if idx <= 0 or icd > cls.ICD_CHAPTER_END[idx - 1]:
                return cls.INVALID_ICD_CHAPTER
            return idx
        return cls.INVALID_ICD_CHAPTER

    @classmethod
    def covid(cls, icd: str) -> Union[str, int]:
        if icd.startswith('B342'):
            return 1  # yes
        if icd.startswith('U04'):
            return 2  # suspected
        if icd.startswith('U99'):
            return cls.INVALID_COVID  # invalid
        return ''  # no

    @classmethod
    def icd_to_cidbr(cls, icd: str) -> str:
        if icd.startswith('O244'):  # special case
            return '089'
        for level in [2, 1, 0]:
            idx = bisect.bisect(cls.CIDBR_LEVELS[level]['begin'], icd[:3])
            if idx > 0 and icd[:3] <= cls.CIDBR_LEVELS[level]['end'][idx - 1]:
                return cls.CIDBR_LEVELS[level]['values'][idx - 1]
        return ''

    @classmethod
    def cidbr_conditions(cls, cidbr: str) -> Dict[str, int]:
        if not cidbr:
            return {}
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
        values = {v: 0 for v in list(named.values()) + ['GPP', 'PERI']}
        cidbr_int = int(cidbr[:3])
        if 88 <= cidbr_int <= 92:
            values['GPP'] = cidbr_int - 87
        elif 93 <= cidbr_int <= 97:
            values['PERI'] = cidbr_int - 92
        else:
            for pfx, name in named.items():
                if cidbr.startswith(pfx):
                    values[name] = 1
        return values

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        icd = row.get('CAUSABAS', None)
        if not icd:
            return {
                'CAPCID': cls.INVALID_ICD_CHAPTER,
                'COVID': cls.INVALID_COVID
            }
        cidbr = cls.icd_to_cidbr(icd)
        return {
            'CAPCID': cls.icd_chapter(icd),
            'COVID': cls.covid(icd),
            'CIDBR': cidbr,
            **cls.cidbr_conditions(cidbr)
        }


# Each new column comes after the column it depends on

COLS_AFTER = {
    'DTOBITO': DeathDateAugmenter.PRODUCES,
    'IDADE': AgeAugmenter.PRODUCES,
    'CODBAIRES': NeighbourhoodAugmenter.PRODUCES,
    'CAUSABAS': DeathCauseAugmenter.PRODUCES
}

ALL_AUGMENTERS = [
    DeathDateAugmenter,
    AgeAugmenter,
    NeighbourhoodAugmenter,
    DeathCauseAugmenter
]


class AugmentedSIM:

    def __init__(self, input_file_name, output_file_name):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name

    def augment(self):
        # Open input file
        parser = TableParser(self.input_file_name)
        cols = parser.columns[:]

        # Add new columns depending on the existing ones
        for existing_column, new_columns in COLS_AFTER.items():
            try:
                idx = cols.index(existing_column)
                for col in reversed(new_columns):
                    cols.insert(idx + 1, col)
            except ValueError:
                pass

        # Open output file
        with open(self.output_file_name, 'w') as fd:
            writer = csv.DictWriter(fd, cols, delimiter=',',
                                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()

            for row in parser.parse():
                parsed_row = SIMRowParser.parse_row(row)
                for augmenter in ALL_AUGMENTERS:
                    row.update(augmenter.get_new_values(parsed_row))

                # write to the CSV file
                writer.writerow(row)


def main():
    desc = '''
    This script reads a DBF or CSV file containing death causes encoded
    according to "Sistema de Informação sobre Mortalidade" (SIM).
    It adds a few columns and saves the file as CSV.
    '''

    # Command-line arguments
    arg_parser = argparse.ArgumentParser(description=desc)
    arg_parser.add_argument('input_file', type=argparse.FileType('r'),
                            help='input file name (DBF or CSV)')
    arg_parser.add_argument('output_file', type=argparse.FileType('w'),
                            help='output file name (CSV)')
    a = arg_parser.parse_args()

    aug = AugmentedSIM(a.input_file.name, a.output_file.name)
    aug.augment()


if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 1:  # No arguments
        from gui.augmented_sim_gui import AugmentedSIMGUI
        AugmentedSIMGUI(augment_cls=AugmentedSIM)
    else:
        main()
