#!/usr/bin/env python3

from typing import Dict
import bisect

from .augmenter import Augmenter


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
