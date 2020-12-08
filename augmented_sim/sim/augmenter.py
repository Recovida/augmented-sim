#!/usr/bin/env python3

from typing import Dict


class Augmenter:
    '''Produces extra columns on a SIM table.'''

    REQUIRES = []
    PRODUCES = []

    @classmethod
    def get_new_values(cls, row: Dict) -> Dict:
        return {}
