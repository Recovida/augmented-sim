#!/usr/bin/env python3
# coding=utf-8

import sys
if sys.version_info < (3, 6):
    print('Este programa requer Python 3.6 ou superior.', file=sys.stderr)
    exit(1)

import os.path

# Support both local and installed execution
# p = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# if p not in sys.path:
#     sys.path.insert(0, p)
#     print(sys.path)

import os
import threading

from typing import List, Callable
from pathlib import Path
from tqdm import tqdm

from table_reader import TableReader
from table_writer import TableWriter
from sim.row_parser import SIMRowParser

from sim.age_augmenter import AgeAugmenter
from sim.death_cause_augmenter import DeathCauseAugmenter
from sim.death_date_augmenter import DeathDateAugmenter
from sim.neighbourhood_augmenter import NeighbourhoodAugmenter


def exception_to_user_friendly_error_message(e):
    import traceback
    tb = traceback.format_exc()
    if isinstance(e, FileNotFoundError):
        return 'Arquivo/caminho inexistente:\n“%s”.' % e.filename
    if isinstance(e, IsADirectoryError):
        return 'O arquivo de saída não pode ser um diretório/pasta.'
    if isinstance(e, PermissionError):
        return 'Não é possível salvar o arquivo no local especificado.\n' \
               'Verifique as permissões.'
    if isinstance(e, OSError):
        import errno
        error = errno.errorcode.get(e.errno, '')
        if error == 'ENOSPC':
            return 'Espaço insuficiente para salvar o arquivo.'
        elif error == 'EROFS':
            return 'Não é possível salvar arquivos ' \
                    'no local especificado: “%s”.' % e.filename
        elif error.endswith('NAMETOOLONG'):
            return 'O nome do arquivo é grande demais:\n“%s”.' % e.filename
        else:
            return os.strerror(e.errno)
    return tb


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
                 parser: TableReader.UNION_ALL_PARSERS,
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
            Path(self.output_file_name).parent.mkdir(
                parents=True, exist_ok=True
            )
            with TableWriter('CSV', self.cols, self.output_file_name) as w:
                w.write_header()
                for row in self.parser.parse():
                    parsed_row = SIMRowParser.parse_row(row)
                    for augmenter in ALL_AUGMENTERS:
                        row.update(augmenter.get_new_values(parsed_row))
                    w.write_row(row)
                    if self.report_progress:
                        self.report_progress(self.parser.progress())
            print('Ok')
        except BaseException as e:
            if self.report_exception:
                msg = exception_to_user_friendly_error_message(e)
                self.report_exception(e, msg)


class AugmentedSIM:

    def __init__(self, input_file_names, output_file_name):
        self.input_file_names = input_file_names
        self.output_file_name = output_file_name

    def augment(self, report_progress=None, report_exception=None):

        # Open input file
        parser = TableReader(self.input_file_names)
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
            overall_pbar.update(-overall_pbar.n + progress[2])
            current_pbar.total = progress[1]
            current_pbar.update(-current_pbar.n + progress[0])
            if progress[2] == progress[3]:
                for bar in [overall_pbar, current_pbar]:
                    bar.close()

        # Open output file
        thread = AugmentThread(
            self.output_file_name, parser, cols, report, report_exception
        )
        thread.start()
