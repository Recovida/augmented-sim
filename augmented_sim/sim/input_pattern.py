#!/usr/bin/env python3

from typing import Dict, List


class InputPattern:

    NAME = ''

    @classmethod
    def adapt_col_list(cls, cols: List[str]) -> List[str]:
        raise NotImplementedError

    @classmethod
    def adapt_row(cls, row: Dict) -> Dict:
        raise NotImplementedError


class Pattern0(InputPattern):

    NAME = '10.2020'

    @classmethod
    def adapt_col_list(cls, cols: List[str]) -> List[str]:
        raise cols[:]

    @classmethod
    def adapt_row(cls, row: Dict) -> Dict:
        raise row.copy()


class Pattern1(InputPattern):

    NAME = '12.2020'

    @classmethod
    def adapt_col_list(cls, cols: List[str]) -> List[str]:
        cols = cols[:]
        try:
            idx = cols.index('ANO_OBITO')
            cols[idx] = 'ANO'
        except ValueError:
            pass
        try:
            idx = cols.index('MES_OBITO')
            cols[idx] = 'MES'
        except ValueError:
            pass
        if 'CD_GEOCODI' in cols and 'CODBAIRES' not in cols:
            cols.insert(cols.index('CD_GEOCODI') + 1, 'CODBAIRES')
        return cols

    @classmethod
    def adapt_row(cls, row: Dict) -> Dict:
        row = row.copy()
        if 'IDADE' in row and row['IDADE']:
            row['IDADE'] = str(400 + int(row['IDADE']))
        if 'MES_OBITO' in row:
            row['MES'] = int(row['MES_OBITO']) if row['MES_OBITO'] else ''
            del row['MES_OBITO']
        if 'ANO_OBITO' in row:
            row['ANO'] = int(row['ANO_OBITO']) if row['ANO_OBITO'] else ''
            del row['ANO_OBITO']
        if 'CD_GEOCODI' in row and 'CODBAIRES' not in row:
            row['CODBAIRES'] = str(row['CD_GEOCODI'])[7:9]
        return row


ALL_PATTERNS = {c.NAME: c for c in [Pattern0, Pattern1]}
