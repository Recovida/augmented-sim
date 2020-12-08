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


def main():
    desc = '''
    This program reads a DBF or CSV file containing death causes encoded
    according to "Sistema de Informação sobre Mortalidade" (SIM).
    It adds a few columns and saves the file as CSV.
    '''

    # Command-line arguments
    arg_parser = argparse.ArgumentParser(description=desc)
    arg_parser.add_argument('output_file', type=argparse.FileType('w'),
                            help='output file name (CSV)')
    arg_parser.add_argument('input_files', nargs='+',
                            type=argparse.FileType('rb'),
                            help='input file names (DBF or CSV)')
    a = arg_parser.parse_args()
    for f in a.input_files + [a.output_file]:
        f.close()

    aug = AugmentedSIM([f.name for f in a.input_files], a.output_file.name)
    aug.augment()


if __name__ == '__main__':
    main()
