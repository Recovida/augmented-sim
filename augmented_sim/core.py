#!/usr/bin/env python3
# coding=utf-8

import sys
if sys.version_info < (3, 6):
    print('Este programa requer Python 3.6 ou superior.', file=sys.stderr)
    exit(1)

import os.path

import os
import threading

from dateutil.relativedelta import relativedelta
from pathlib import Path
from tqdm import tqdm
from typing import List, Callable

from augmented_sim.table_reader import TableReader
from augmented_sim.table_writer import TableWriter
from augmented_sim.sim.row_parser import SIMRowParser

from augmented_sim.sim.age_augmenter import AgeAugmenter
from augmented_sim.sim.death_cause_augmenter import DeathCauseAugmenter
from augmented_sim.sim.death_date_augmenter import DeathDateAugmenter
from augmented_sim.sim.neighbourhood_augmenter import NeighbourhoodAugmenter


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
                 report_exception: Callable[[BaseException, str], None] = None,
                 report_conclusion: Callable[[], None] = None
                 ):
        super().__init__()
        self.output_file_name = output_file_name
        self.parser = parser
        self.cols = cols
        self.report_progress = report_progress
        self.report_exception = report_exception
        self.report_conclusion = report_conclusion

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
                if self.report_progress:
                    self.report_progress(self.parser.progress())
            if self.report_conclusion:
                self.report_conclusion()
        except BaseException as e:
            if self.report_exception:
                msg = exception_to_user_friendly_error_message(e)
                self.report_exception(e, msg)


class AugmentedSIM:

    def __init__(self, input_file_names, output_file_name):
        self.input_file_names = input_file_names
        self.output_file_name = output_file_name

    def augment(self,
                report_progress: Callable[[List], None] = None,
                report_exception: Callable[[BaseException, str], None] = None,
                report_conclusion: Callable[[str], None] = None):

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
        fmt = '{l_bar}{bar} {remaining}'
        overall_pbar = tqdm(
            total=progress[3], bar_format=fmt, colour='green',
            desc='OVERALL',  position=0, leave=False
        )
        current_pbar = tqdm(
            total=progress[1], bar_format=fmt, colour='green',
            desc='CURRENT', position=1, leave=False
        )

        def _report_progress(progress):
            if report_progress:
                report_progress(progress)
            overall_pbar.update(-overall_pbar.n + progress[2])
            current_pbar.total = progress[1]
            current_pbar.update(-current_pbar.n + progress[0])

        def _report_exception(exc, msg):
            print(msg)
            report_exception(exc, msg)

        def _format_elapsed_time(dt):
            # Report elapsed time (in Portuguese)
            t_str = []
            expr = [
                ('days', 'd'), ('hours', 'h'),
                ('minutes', 'min'), ('seconds', 's')
            ]
            for attr, symbol in expr:
                value = getattr(dt, attr)
                if symbol == 's' and len(t_str) == 0:
                    value = round(value, 3)
                else:
                    value = int(value)
                if value > 0:
                    t_str.append(str(value).replace('.', ',') + symbol)
            if len(t_str) == 0:
                t_str = ['0s']
            return ''.join(t_str)

        def _report_conclusion():
            for bar in [overall_pbar, current_pbar]:
                bar.close()
                print()  # fix cursor position
            elapsed = overall_pbar.format_dict['elapsed']
            if report_conclusion:
                report_conclusion(elapsed)
            # Using an integer to get integer attributes later
            dt = relativedelta(seconds=elapsed)
            s = _format_elapsed_time(dt)
            print(f'Arquivo salvo (tempo decorrido: {s}).')

        # Open output file
        thread = AugmentThread(
            self.output_file_name, parser, cols,
            _report_progress, _report_exception, _report_conclusion
        )
        thread.start()
