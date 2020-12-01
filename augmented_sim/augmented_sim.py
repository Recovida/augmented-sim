#!/usr/bin/env python3

import argparse
import bisect
import csv
import dbfread
import datetime
import os
import threading

from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple, Union, Dict, List, Callable

try:
    from tqdm import tqdm  # optional, for progress display
except Exception:
    pass


class TableParser:
    '''Reads a DBF or CSV table.'''

    def __init__(self, file_names: str):
        self.files = []
        self.columns = []
        self.read_count = {}
        self.currently_reading = ''
        self.finished = False
        for file_name in file_names:
            self.read_count[file_name] = 0
            if file_name.lower().endswith('.csv'):
                format = 'CSV'
                fd = open(file_name, 'r', encoding='utf-8-sig')
                dialect = csv.Sniffer().sniff(fd.read(1024))
                fd.seek(0, os.SEEK_END)
                denominator = fd.tell()
                fd.seek(0)
                parser = csv.DictReader(iter(fd.readline, ''), dialect=dialect)
                columns = parser.fieldnames
                get_pos = (lambda fd: lambda: fd.tell())(fd)
            elif file_name.lower().endswith('.dbf'):
                format = 'DBF'
                parser = dbfread.DBF(file_name)
                columns = parser.field_names[:]
                denominator = parser.header.numrecords
                get_pos = (lambda fn: lambda: self.read_count[fn])(file_name)
            else:
                raise Exception('Formato não suportado.')
            self.files.append(
                [file_name, format, parser, columns, get_pos, 0, denominator]
            )
            for column in columns:
                if column not in self.columns:
                    self.columns.append(column)

    def parse(self):
        self.finished = False
        for f in self.files:
            file_name, format, parser, columns, get_pos, num, den = f
            self.currently_reading = file_name
            for row in parser:
                self.read_count[file_name] += 1
                f[-2] = min(den, get_pos())
                yield row
        self.currently_reading = ''
        self.finished = True

    def progress(self):
        overall_num = 0
        overall_den = 0
        current = None
        try:
            for f in self.files:
                file_name, format, parser, columns, get_pos, num, den = f
                overall_num += num / den
                overall_den += 1
                if current is None and num < den:
                    current = (num, den)
        except Exception:
            return (0, 1, 0, 1, '')
        else:
            if current is None:
                current = (overall_num and 1, 1)
            return (*current, overall_num, overall_den, self.currently_reading)


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
            return int(value)
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
        'IDADECAT1',      # age category I (1..20)
        'IDADECAT2'       # age category II (1..8)
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
                1 if age.years < 1 else min(20, 2 + age.years // 5),
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
        70: 1, 71: 1, 72: 1, 73: 2, 74: 2, 75: 3, 76: 3, 77: 3, 78: 3, 79: 1,
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
        'GARBAGECODE',  # garbage code (0..4)
        'CAPCID',       # ICD chapter (integer)
        'COVID',        # COVID-19 (0=missing/no, 1=yes, 2=suspected)
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

    GARBAGE_CODE_LEVELS = {1: {}, 2: {}, 3: {}, 4: {}}
    GARBAGE_CODE_LEVELS[1]['begin'] = [
        'A40', 'A480', 'A483', 'A490', 'A59', 'A71', 'A740', 'B07', 'B30',
        'B35', 'B85', 'B87', 'B940', 'D50', 'D509', 'D62', 'D638', 'D641',
        'D648', 'D68', 'D699', 'E15', 'E16', 'E50', 'E641', 'E853', 'E878',
        'F062', 'F072', 'F09', 'F17', 'F20', 'F25', 'F51', 'G06', 'G32',
        'G43', 'G444', 'G47', 'G474', 'G50', 'G62', 'G80', 'G89', 'G91',
        'G914', 'G931', 'G934', 'G99', 'H052', 'H71', 'I26', 'I312', 'I46',
        'I50', 'I517', 'I674', 'I76', 'I95', 'I958', 'J69', 'J80', 'J85',
        'J86', 'J93', 'J938', 'J942', 'J96', 'J981', 'K00', 'K30', 'K65',
        'K669', 'K71', 'K718', 'K750', 'L20', 'L40', 'L52', 'L56', 'L564',
        'L57', 'L59', 'L70', 'L80', 'L90', 'L94', 'L985', 'M04', 'M10',
        'M122', 'M37', 'M432', 'M492', 'M651', 'M712', 'M728', 'M738',
        'M83', 'M865', 'M872', 'M891', 'M90', 'N17', 'N19', 'N321', 'N328',
        'N35', 'N37', 'N393', 'N42', 'N441', 'N46', 'N50', 'N61', 'N82',
        'N91', 'N95', 'N951', 'N97', 'R02', 'R031', 'R070', 'R08', 'R093',
        'R11', 'R14', 'R19', 'R198', 'R231', 'R32', 'R508', 'R580', 'R74',
        'R786', 'R96', 'U05', 'U07', 'U90', 'X40', 'X470', 'X479', 'X49',
        'Y10', 'Z00', 'Z17',
    ]
    GARBAGE_CODE_LEVELS[1]['end'] = [
        'A419', 'A480', 'A483', 'A490', 'A599', 'A719', 'A740', 'B079',
        'B309', 'B369', 'B854', 'B889', 'B940', 'D500', 'D509', 'D630',
        'D64', 'D642', 'D659', 'D68', 'D699', 'E15', 'E16', 'E509', 'E641',
        'E876', 'E879', 'F064', 'F072', 'F099', 'F179', 'F239', 'F49',
        'F990', 'G080', 'G328', 'G442', 'G448', 'G472', 'G479', 'G609',
        'G652', 'G839', 'G894', 'G912', 'G929', 'G932', 'G936', 'H05',
        'H699', 'H99', 'I269', 'I314', 'I469', 'I509', 'I517', 'I674',
        'I76', 'I951', 'I959', 'J699', 'J809', 'J853', 'J869', 'J931',
        'J939', 'J942', 'J969', 'J983', 'K19', 'K30', 'K661', 'K669',
        'K711', 'K720', 'K750', 'L309', 'L509', 'L540', 'L562', 'L565',
        'L579', 'L689', 'L768', 'L879', 'L929', 'L96', 'L998', 'M04',
        'M120', 'M29', 'M39', 'M49', 'M64', 'M71', 'M724', 'M73', 'M799',
        'M862', 'M869', 'M879', 'M894', 'M999', 'N179', 'N199', 'N322',
        'N338', 'N359', 'N378', 'N398', 'N434', 'N448', 'N489', 'N539',
        'N649', 'N829', 'N915', 'N95', 'N959', 'N979', 'R029', 'R031',
        'R070', 'R09', 'R093', 'R120', 'R159', 'R196', 'R23', 'R309',
        'R501', 'R579', 'R729', 'R78', 'R948', 'R999', 'U05', 'U81', 'U99',
        'X449', 'X470', 'X479', 'X499', 'Y199', 'Z158', 'Z17',
    ]
    GARBAGE_CODE_LEVELS[2]['begin'] = [
        'A149', 'A29', 'A45', 'A47', 'A488', 'A493', 'A61', 'A72', 'A76',
        'A97', 'B08', 'B11', 'B28', 'B31', 'B34', 'B61', 'B68', 'B73',
        'B76', 'B78', 'B84', 'B93', 'B948', 'B956', 'B977', 'D59', 'D594',
        'D598', 'G443', 'G913', 'G930', 'G933', 'I10', 'I15', 'I27',
        'I272', 'I289', 'I70', 'I709', 'I74', 'J81', 'J90', 'J94', 'J948',
        'K920', 'N70', 'N73', 'N743', 'R03', 'R04', 'R090', 'R098', 'R13',
        'R16', 'R230', 'R58', 'S00', 'W47', 'W63', 'W71', 'W76', 'W82',
        'W95', 'W98', 'X07', 'X55', 'X59', 'Y20', 'Y86', 'Y872', 'Y89',
        'Y899',
    ]
    GARBAGE_CODE_LEVELS[2]['end'] = [
        'A149', 'A29', 'A459', 'A48', 'A49', 'A499', 'A62', 'A73', 'A76',
        'A97', 'B09', 'B14', 'B29', 'B324', 'B349', 'B62', 'B689', 'B742',
        'B769', 'B818', 'B84', 'B94', 'B949', 'B973', 'B999', 'D59',
        'D594', 'D599', 'G443', 'G913', 'G930', 'G933', 'I109', 'I159',
        'I270', 'I279', 'I289', 'I701', 'I709', 'I758', 'J811', 'J900',
        'J941', 'J949', 'K922', 'N719', 'N740', 'N748', 'R030', 'R069',
        'R092', 'R109', 'R139', 'R189', 'R230', 'R58', 'S00', 'W48', 'W63',
        'W72', 'W769', 'W82', 'W97', 'W98', 'X07', 'X56', 'X599', 'Y349',
        'Y87', 'Y872', 'Y89', 'Y999',
    ]
    GARBAGE_CODE_LEVELS[3]['begin'] = [
        'A01', 'A31', 'A42', 'A492', 'A64', 'A99', 'B37', 'B49', 'B551',
        'B58', 'B89', 'C14', 'C26', 'C35', 'C39', 'C42', 'C46', 'C55',
        'C579', 'C59', 'C639', 'C68', 'C689', 'C759', 'C87', 'C97', 'D01',
        'D014', 'D024', 'D07', 'D073', 'D076', 'D091', 'D097', 'D099',
        'D109', 'D13', 'D139', 'D144', 'D17', 'D28', 'D289', 'D299',
        'D309', 'D360', 'D369', 'D376', 'D386', 'D397', 'D399', 'D409',
        'D419', 'D44', 'D449', 'D48', 'D487', 'D495', 'D497', 'D54',
        'D759', 'D79', 'D87', 'D898', 'E078', 'E17', 'E349', 'E37', 'E47',
        'E62', 'E69', 'E877', 'E90', 'F04', 'F065', 'F078', 'F50', 'F508',
        'G09', 'G15', 'G27', 'G33', 'G38', 'G42', 'G48', 'G66', 'G74',
        'G84', 'G93', 'G938', 'G96', 'G98', 'I000', 'I03', 'I14', 'I16',
        'I29', 'I44', 'I49', 'I51', 'I516', 'I518', 'I90', 'I96', 'I984',
        'I99', 'J02', 'J028', 'J038', 'J041', 'J051', 'J48', 'J71', 'J819',
        'J83', 'J859', 'J87', 'J909', 'J936', 'J97', 'J984', 'K319', 'K39',
        'K47', 'K53', 'K63', 'K638', 'K69', 'K75', 'K78', 'K84', 'K87',
        'K92', 'K929', 'K96', 'L06', 'L09', 'L15', 'L31', 'L69', 'L77',
        'N09', 'N13', 'N24', 'N288', 'N38', 'N399', 'N54', 'N66', 'N78',
        'N84', 'N842', 'N88', 'N92', 'N950', 'O08', 'O17', 'O27', 'O37',
        'O49', 'O78', 'O93', 'P06', 'P16', 'P30', 'P40', 'P62', 'P73',
        'P79', 'P82', 'P85', 'P969', 'Q08', 'Q19', 'Q29', 'Q360', 'Q46',
        'Q88', 'Q899', 'Q94', 'Q999', 'R07', 'R071', 'R31',
    ]
    GARBAGE_CODE_LEVELS[3]['end'] = [
        'A01', 'A319', 'A449', 'A492', 'A640', 'A990', 'B469', 'B499',
        'B552', 'B599', 'B89', 'C149', 'C29', 'C36', 'C399', 'C42', 'C469',
        'C559', 'C579', 'C59', 'C639', 'C68', 'C689', 'C809', 'C87',
        'D000', 'D01', 'D02', 'D029', 'D07', 'D073', 'D09', 'D091', 'D097',
        'D10', 'D109', 'D13', 'D14', 'D144', 'D219', 'D28', 'D29', 'D30',
        'D309', 'D360', 'D370', 'D38', 'D390', 'D397', 'D40', 'D41',
        'D419', 'D44', 'D449', 'D48', 'D491', 'D495', 'D499', 'D54',
        'D759', 'D85', 'D88', 'D99', 'E089', 'E19', 'E358', 'E39', 'E49',
        'E62', 'E69', 'E877', 'E998', 'F061', 'F070', 'F08', 'F50', 'F509',
        'G099', 'G19', 'G29', 'G34', 'G39', 'G42', 'G49', 'G69', 'G79',
        'G88', 'G93', 'G948', 'G969', 'G989', 'I000', 'I04', 'I14', 'I19',
        'I299', 'I459', 'I499', 'I51', 'I516', 'I59', 'I94', 'I969',
        'I988', 'J000', 'J02', 'J03', 'J04', 'J043', 'J069', 'J59', 'J79',
        'J819', 'J83', 'J859', 'J89', 'J909', 'J936', 'J980', 'J998',
        'K34', 'K39', 'K49', 'K54', 'K634', 'K639', 'K69', 'K75', 'K79',
        'K84', 'K89', 'K92', 'K93', 'K99', 'L07', 'L09', 'L19', 'L39',
        'L69', 'L79', 'N09', 'N139', 'N24', 'N289', 'N38', 'N409', 'N59',
        'N69', 'N79', 'N84', 'N86', 'N909', 'N949', 'N950', 'O089', 'O19',
        'O27', 'O39', 'O59', 'O79', 'O959', 'P06', 'P18', 'P342', 'P49',
        'P69', 'P73', 'P79', 'P82', 'P89', 'P999', 'Q103', 'Q19', 'Q29',
        'Q369', 'Q49', 'Q88', 'Q899', 'Q94', 'R012', 'R07', 'R079', 'R319',
    ]
    GARBAGE_CODE_LEVELS[4]['begin'] = [
        'B54', 'B559', 'B64', 'B82', 'B839', 'D471', 'G00', 'G009', 'G039',
        'I42', 'I429', 'I515', 'I64', 'I67', 'I678', 'I688', 'I694', 'J07',
        'J159', 'J17', 'J22', 'J64', 'P23', 'P235', 'P373', 'V87', 'V874',
        'V884', 'V99', 'Y09', 'Y85',
    ]
    GARBAGE_CODE_LEVELS[4]['end'] = [
        'B55', 'B559', 'B64', 'B829', 'B839', 'D471', 'G00', 'G028',
        'G039', 'I420', 'I429', 'I515', 'I649', 'I67', 'I68', 'I69',
        'I699', 'J08', 'J159', 'J196', 'J29', 'J649', 'P23', 'P239',
        'P374', 'V871', 'V881', 'V899', 'V990', 'Y099', 'Y859',
    ]

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
    def covid(cls, icd: str) -> int:
        if icd.startswith('B342'):
            return 1  # yes
        if icd.startswith('U04'):
            return 2  # suspected
        if icd.startswith('U99'):
            return cls.INVALID_COVID  # invalid
        return 0  # no

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
    def garbage_code(cls, icd: str) -> str:
        for level in range(4, 0, -1):
            gc = cls.GARBAGE_CODE_LEVELS[level]
            idx = bisect.bisect(gc['begin'], icd)
            last = gc['end'][idx - 1]
            if idx > 0 and icd[:len(last)] <= last:
                return level
        return 0

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        icd = row.get('CAUSABAS', None)
        if not icd:
            return {
                'CAPCID': cls.INVALID_ICD_CHAPTER,
                'COVID': cls.INVALID_COVID
            }
        cidbr = cls.icd_to_cidbr(icd)
        if 'DTOBITO' in row and row['DTOBITO'].year < 2020:
            covid = 0
        else:
            covid = cls.covid(icd)
        return {
            'GARBAGECODE': cls.garbage_code(icd),
            'CAPCID': cls.icd_chapter(icd),
            'COVID': covid,
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


class AugmentThread(threading.Thread):

    def __init__(self,
                 output_file_name: str,
                 parser: Union[csv.DictReader, dbfread.DBF],
                 cols: List[str],
                 report_progress: Callable[[List], None] = None,
                 report_exception: Callable[[BaseException], str] = None
                 ):
        super().__init__()
        self.output_file_name = output_file_name
        self.parser = parser
        self.cols = cols
        self.report_progress = report_progress
        self.report_exception = report_exception

    def run(self):
        self.exception = None
        try:
            if self.report_progress:
                self.report_progress(self.parser.progress())
            with open(self.output_file_name, 'w') as fd:
                writer = csv.DictWriter(fd, self.cols, delimiter=',',
                                        quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for row in self.parser.parse():
                    parsed_row = SIMRowParser.parse_row(row)
                    for augmenter in ALL_AUGMENTERS:
                        row.update(augmenter.get_new_values(parsed_row))
                    writer.writerow(row)
                    if self.report_progress:
                        self.report_progress(self.parser.progress())
            print('Ok')
        except BaseException as e:
            if self.report_exception:
                import traceback
                self.report_exception(e, traceback.format_exc())


class AugmentedSIM:

    def __init__(self, input_file_names, output_file_name):
        self.input_file_names = input_file_names
        self.output_file_name = output_file_name

    def augment(self, report_progress=None, report_exception=None):

        # Open input file
        parser = TableParser(self.input_file_names)
        cols = parser.columns[:]

        # Add new columns depending on the existing ones
        for existing_column, new_columns in COLS_AFTER.items():
            try:
                idx = cols.index(existing_column)
                for col in reversed(new_columns):
                    cols.insert(idx + 1, col)
            except ValueError:
                pass

        # Progress
        if tqdm:
            progress = parser.progress()
            fmt = '{l_bar}{bar}'
            overall_pbar = tqdm(
                total=progress[3], bar_format=fmt, colour='green',
                desc='OVERALL',  position=0, leave=False
            )
            current_pbar = tqdm(
                total=progress[1], bar_format=fmt, colour='green',
                desc='CURRENT', position=1, leave=False
            )

            def report(progress):
                if report_progress:
                    report_progress(progress)
                if tqdm:
                    overall_pbar.update(-overall_pbar.n + progress[2])
                    current_pbar.total = progress[1]
                    current_pbar.update(-current_pbar.n + progress[0])
                if progress[2] == progress[3]:
                    if tqdm:
                        for bar in [overall_pbar, current_pbar]:
                            bar.close()

        # Open output file
        thread = AugmentThread(
            self.output_file_name, parser, cols, report, report_exception
        )
        thread.start()


def main():
    desc = '''
    This script reads a DBF or CSV file containing death causes encoded
    according to "Sistema de Informação sobre Mortalidade" (SIM).
    It adds a few columns and saves the file as CSV.
    '''

    # Command-line arguments
    arg_parser = argparse.ArgumentParser(description=desc)
    arg_parser.add_argument('output_file', type=argparse.FileType('w'),
                            help='output file name (CSV)')
    arg_parser.add_argument('input_files', nargs='+',
                            type=argparse.FileType('rb'),
                            help='input file names (DBF or CSV)')
    a = arg_parser.parse_args()
    for f in a.input_files + [a.output_file]:
        f.close()

    aug = AugmentedSIM([f.name for f in a.input_files], a.output_file.name)
    aug.augment()


if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 1:  # No arguments
        from gui.augmented_sim_gui import AugmentedSIMGUI
        AugmentedSIMGUI(augment_cls=AugmentedSIM)
    else:
        main()
