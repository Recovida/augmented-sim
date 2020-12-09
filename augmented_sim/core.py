#!/usr/bin/env python3
# coding=utf-8

import sys
if sys.version_info < (3, 6):
    print('Este programa requer Python 3.6 ou superior.', file=sys.stderr)
    exit(1)

import threading

from dateutil.relativedelta import relativedelta
from pathlib import Path
from tqdm import tqdm
from time import time
from typing import List, Callable, Union

from augmented_sim.table_reader import TableReader
from augmented_sim.table_writer import TableWriter
from augmented_sim.sim.row_parser import SIMRowParser

from augmented_sim.sim.age_augmenter import AgeAugmenter
from augmented_sim.sim.death_cause_augmenter import DeathCauseAugmenter
from augmented_sim.sim.death_date_augmenter import DeathDateAugmenter
from augmented_sim.sim.neighbourhood_augmenter import NeighbourhoodAugmenter


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
                 report_exception: Callable[[BaseException], None] = None,
                 report_conclusion: Callable[[], None] = None
                 ):
        super().__init__()
        self.output_file_name = output_file_name
        self.parser = parser
        self.cols = cols
        self.report_progress = report_progress
        self.report_exception = report_exception
        self.report_conclusion = report_conclusion

    def run(self) -> None:
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
        except Exception as e:
            if self.report_exception:
                self.report_exception(e)


class AugmentedSIM:

    def __init__(self, input_file_names: str, output_file_name: str):
        self.input_file_names = input_file_names
        self.output_file_name = output_file_name

    def augment(self,
                report_progress: Callable[[List], None] = None,
                report_exception: Callable[[BaseException], None] = None,
                report_conclusion: Callable[[str], None] = None) -> None:

        start_time = time()

        # Progress
        fmt = '{l_bar}{bar} {remaining}'
        disable = 'pythonw' in sys.executable  # avoid crash on Windows
        overall_pbar = tqdm(
            bar_format=fmt, colour='green',
            desc='OVERALL', position=0, leave=False, disable=disable
        )
        current_pbar = tqdm(
            bar_format=fmt, colour='green',
            desc='CURRENT', position=1, leave=False, disable=disable
        )

        def _report_progress(progress: Union[int, float]) -> None:
            if report_progress:
                report_progress(progress)
            overall_pbar.update(-overall_pbar.n + progress[2])
            current_pbar.total = progress[1]
            current_pbar.update(-current_pbar.n + progress[0])

        def _report_exception(exc: str) -> None:
            for bar in [overall_pbar, current_pbar]:
                bar.close()
            report_exception(exc)

        def _format_elapsed_time(dt: relativedelta) -> str:
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

        def _report_conclusion() -> None:
            for bar in [overall_pbar, current_pbar]:
                bar.close()
                if not bar.disable:
                    print('\n')  # fix cursor position
            elapsed = time() - start_time
            if report_conclusion:
                report_conclusion(elapsed)
            # Using an integer to get integer attributes later
            dt = relativedelta(seconds=elapsed)
            s = _format_elapsed_time(dt)
            print(f'Arquivo salvo (tempo decorrido: {s}).')

        # Open input file
        try:
            parser = TableReader(self.input_file_names)
        except Exception as e:
            _report_exception(e)
            return

        cols = parser.columns[:]
        progress = parser.progress()

        # Add new columns depending on the existing ones
        for existing_column, new_columns in COLS_AFTER.items():
            try:
                idx = cols.index(existing_column)
                for col in reversed(new_columns):
                    cols.insert(idx + 1, col)
            except ValueError:
                pass

        overall_pbar.total = progress[3]
        current_pbar.total = progress[1]

        # Open output file
        thread = AugmentThread(
            self.output_file_name, parser, cols,
            _report_progress, _report_exception, _report_conclusion
        )
        thread.start()
