#!/usr/bin/env python3

from bs4 import BeautifulSoup as BS
from typing import List

import bisect
import re


with open('obtcid10br.htm', 'r', encoding='ISO8859') as fd:
    h = BS(fd, 'lxml')

table = h.find('table', class_='tabdados')

levels = {}
for lvl in [0, 1, 2]:
    levels[lvl] = {'begin': [], 'end': [], 'values': []}

for row in table.tbody.find_all('tr'):
    # rows with chapter number have an extra column in the beginning
    cidbr_col, label_col, icd_col = row.find_all('td')[-3:]

    cidbr = cidbr_col.get_text().strip()
    if '-' in cidbr:
        continue

    icd = icd_col.get_text().strip().replace(' ', '').replace('\n', '')
    icd = icd.replace('O24.4,', '')  # we'll deal with O24.4 separately
    icd = icd.replace('N016', 'N16')  # there's a typo on the table
    icd = re.sub(r'\(exceto[^\)]+\)', '', icd).strip(',')

    # to get the nesting level, check 'padding-left'
    style = cidbr_col.get('style', '')
    level = int(style[14]) if style else 0

    for rng in icd.split(','):
        if len(rng) == 3:
            rng = rng + '-' + rng
        begin = rng[:3]
        end = rng[-3:]
        assert(len(begin) == 3 and len(end) == 3)
        pos = bisect.bisect(levels[level]['begin'], begin)
        levels[level]['begin'].insert(pos, begin)
        levels[level]['end'].insert(pos, end)
        levels[level]['values'].insert(pos, cidbr)


def print_list(elements: List, limit: int = 74) -> None:
    s = ''
    for element in elements:
        p = f"'{element}', "
        if len(s) + len(p) > limit:
            print('    ' + s)
            s = ''
        s += p
    print('    ' + s)


for level, dictionary in levels.items():
    for name, elements in dictionary.items():
        print(f"CIDBR_LEVELS[{level}]['{name}'] = [")
        print_list(elements)
        print(']')
