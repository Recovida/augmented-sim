#!/usr/bin/env python3

from typing import Dict

from .augmenter import Augmenter


class NeighbourhoodAugmenter(Augmenter):

    REQUIRES = ['CODBAIRES']
    PRODUCES = [
        'AREARENDA',      # neighbourhood income (ALTA/INTERMEDIARIA/BAIXA)
    ]

    neighbourhood_income_table = {
        1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 1, 7: 1, 8: 1, 9: 2,
        10: 2, 11: 3, 12: 1, 13: 3, 14: 1, 15: 1, 16: 1, 17: 3, 18: 2, 19: 3,
        20: 2, 21: 2, 22: 3, 23: 3, 24: 3, 25: 3, 26: 1, 27: 1, 28: 3, 29: 2,
        30: 3, 31: 3, 32: 3, 33: 1, 34: 1, 35: 1, 36: 3, 37: 2, 38: 3, 39: 2,
        40: 2, 41: 3, 42: 3, 43: 3, 44: 1, 45: 3, 46: 2, 47: 3, 48: 1, 49: 1,
        50: 2, 51: 1, 52: 3, 53: 1, 54: 1, 55: 1, 56: 3, 57: 2, 58: 3, 59: 3,
        60: 2, 61: 1, 62: 3, 63: 1, 64: 2, 65: 2, 66: 2, 67: 1, 68: 2, 69: 2,
        70: 1, 71: 1, 72: 1, 73: 2, 74: 2, 75: 3, 76: 3, 77: 3, 78: 3, 79: 1,
        80: 2, 81: 1, 82: 1, 83: 3, 84: 1, 85: 2, 86: 3, 87: 2, 88: 2, 89: 3,
        90: 1, 91: 2, 92: 1, 93: 2, 94: 2, 95: 2, 96: 1
    }
    # neighbourhood_income_names = {1: 'ALTA', 2: 'INTERMEDIARIA', 3: 'BAIXA'}

    @classmethod
    def neighbourhood_income(cls, neighbourhood: int) -> int:
        income_id = cls.neighbourhood_income_table.get(neighbourhood, 0)
        # return cls.neighbourhood_income_names.get(income_id, None)
        return income_id

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        neighbourhood = row.get('CODBAIRES', None)
        if neighbourhood is None:
            return {}
        income = cls.neighbourhood_income(neighbourhood)
        return {
            'AREARENDA': income
        } if income else {}
