#!/usr/bin/env python3

import datetime

from dateutil.relativedelta import relativedelta
from typing import Optional, Dict


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
            return relativedelta(**{args[unit]: value}).normalized()
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
    def parse_row(cls, row: Dict) -> Dict:
        converters = {
            'DTOBITO': cls.parse_date,
            'IDADE': cls.parse_age,
            'CODBAIRES': cls.parse_int,
            'CAUSABAS': cls.parse_icd
        }
        return {k: converters.get(k, lambda x: x)(v) for k, v in row.items()}
