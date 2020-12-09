#!/usr/bin/env python3
# coding=utf-8

import argparse
import sys

if vars(sys.modules[__name__])['__package__'] is None and \
        __name__ == '__main__':
    # allow running from any folder
    import pathlib
    here = pathlib.Path(__file__).parent.parent.resolve()
    sys.path.insert(1, str(here))


from augmented_sim.core import AugmentedSIM


def main() -> None:
    desc = '''
    This program reads a DBF or CSV file containing death causes encoded
    according to "Sistema de Informação sobre Mortalidade" (SIM).
    It adds a few columns and saves the file as CSV.
    '''

    # Command-line arguments
    arg_parser = argparse.ArgumentParser(description=desc)
    arg_parser.add_argument('output_file', type=str,
                            help='output file name (CSV)')
    arg_parser.add_argument('input_files', nargs='+',
                            type=str,
                            help='input file names (DBF or CSV)')
    a = arg_parser.parse_args()

    def on_exc(e: BaseException) -> None:
        msg = getattr(e, 'message', str(e))
        details = getattr(e, 'details', '')
        print('=====', msg, '\n', details, '\n\n')

    aug = AugmentedSIM(a.input_files, a.output_file)
    aug.augment(report_exception=on_exc)


if __name__ == '__main__':
    main()
