import pathlib
import os
import re

PROGRAM_METADATA = {}

GIT_URL = 'https://gitlab.com/projeto-fm-usp-mortalidade-sp/' \
          'augmented-sim/-/blob/master/README.md'
PROJECT_DESCRIPTION = '''
Este programa está sendo desenvolvido como parte do projeto
[*Reavaliação da Mortalidade por Causas Naturais no Município de São Paulo
durante a Pandemia da
COVID-19*](https://gitlab.com/projeto-fm-usp-mortalidade-sp/index),
da
[Faculdade de Medicina da Universidade de São Paulo](https://www.fm.usp.br/),
sob responsabilidade do Prof. Dr. Paulo Andrade Lotufo (palotufo@usp.br).

#### Equipe de desenvolvimento:

- Débora Lina Nascimento Ciriaco Pereira (bolsista de dez/2020 a jul/2021);
- Vinícius Bitencourt Matos (bolsista de dez/2020 a jul/2021).'''.strip()


def define_values():
    here = pathlib.Path(__file__).parent.resolve()
    with open(here.parent/'LICENCE.txt', 'r', encoding='utf-8') as fd:
        PROGRAM_METADATA['LICENCE_TEXT'] = fd.read()
    with open(here.parent/'README.md', 'r', encoding='utf-8') as fd:
        PROGRAM_METADATA['READ_ME'] = fd.read() \
            .split('<!-- ABOUT:END -->')[0].split('<!-- ABOUT:BEGIN -->')[-1] \
            + '<br/> <br/> \n \n' + f'[Documentação]({GIT_URL})'
    directory = here / '.licences'
    PROGRAM_METADATA['LICENCES'] = []
    for f in sorted(os.listdir(directory)):
        if re.match(r'^\d\d_.+', f):
            with open(directory/f, 'r', encoding='utf-8') as fd:
                PROGRAM_METADATA['LICENCES'].append((f[3:], fd.read()))
    PROGRAM_METADATA['PROJECT_DESCRIPTION'] = PROJECT_DESCRIPTION


define_values()
