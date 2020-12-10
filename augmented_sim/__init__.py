import pathlib
import os
import re

__version__ = '0.0.1.dev1'
__year__ = 2020

NAME = 'Augmented SIM'
DESCRIPTION = 'Programa que adiciona colunas a uma tabela de óbitos' \
              ' codificados segundo o SIM'

GIT_URL = 'https://gitlab.com/projeto-fm-usp-mortalidade-sp/' \
          'augmented-sim/-/blob/master/README.md'

here = pathlib.Path(__file__).parent.resolve()


LONG_DESCRIPTION = (here.parent / 'README.md').read_text(encoding='utf-8')

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


PROGRAM_METADATA = {}


def define_values() -> None:
    PROGRAM_METADATA['NAME'] = NAME
    PROGRAM_METADATA['VERSION'] = __version__
    PROGRAM_METADATA['YEAR'] = __year__
    PROGRAM_METADATA['LICENCE_TEXT'] = (here.parent / 'LICENCE.txt') \
        .read_text(encoding='utf-8')
    PROGRAM_METADATA['READ_ME'] = (here.parent / 'README.md') \
        .read_text(encoding='utf-8') \
        .split('<!-- ABOUT:END -->')[0].split('<!-- ABOUT:BEGIN -->')[-1] \
        + '<br/> <br/> \n \n' + f'[Documentação]({GIT_URL})'
    directory = here / '.licences'
    PROGRAM_METADATA['LICENCES'] = []
    for f in sorted(os.listdir(directory)):
        if re.match(r'^\d\d_.+', f):
            licence = (directory / f).read_text(encoding='utf-8')
            PROGRAM_METADATA['LICENCES'].append((f[3:], licence))
    PROGRAM_METADATA['PROJECT_DESCRIPTION'] = PROJECT_DESCRIPTION


define_values()
