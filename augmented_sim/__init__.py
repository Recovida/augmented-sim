import pathlib
import os
import re

PROGRAM_METADATA = {}


def define_values():
    here = pathlib.Path(__file__).parent.resolve()
    with open(here.parent/'LICENCE.txt', 'r', encoding='utf-8') as fd:
        PROGRAM_METADATA['LICENCE_TEXT'] = fd.read()
    with open(here.parent/'README.md', 'r', encoding='utf-8') as fd:
        PROGRAM_METADATA['READ_ME'] = fd.read().split('<!-- ABOUT:END -->')[0]
    directory = here / '.licences'
    PROGRAM_METADATA['LICENCES'] = []
    for f in sorted(os.listdir(directory)):
        if re.match(r'^\d\d_.+', f):
            with open(directory/f, 'r', encoding='utf-8') as fd:
                PROGRAM_METADATA['LICENCES'].append((f[3:], fd.read()))


define_values()
