#!/usr/bin/env python3
# coding=utf-8

import csv
import os


class TableWritingError(Exception):

    def __init__(self, message, file_name, orig_exception=None):
        super().__init__(message or f'Não foi possível salvar “{file_name}”.')
        self.message = message
        self.file_name = file_name
        self.orig_exception = orig_exception
        self.details = ''
        if orig_exception:
            import traceback
            tb = traceback.TracebackException.from_exception(orig_exception)
            self.details = ''.join(tb.format())


def handle_table_writing_exceptions(function):
    def f(*args, **kwargs):
        if hasattr(args[0], 'file_name'):
            file_name = args[0].file_name
        else:  # constructor of TableWriter
            file_name = args[3]
        try:
            function(*args, **kwargs)
        except FileNotFoundError as e:
            raise TableWritingError(
                    'Arquivo ou caminho inexistente ou '
                    f'inválido:\n“{e.filename}”.',
                    e.filename, e
            )
        except IsADirectoryError as e:
            raise TableWritingError(
                    'O arquivo de saída não pode ser um diretório/pasta.',
                    e.filename, e
            )
        except PermissionError as e:
            raise TableWritingError(
                    'Não é possível salvar o arquivo no local especificado.'
                    '\nVerifique as permissões.',
                    e.filename, e
            )
        except OSError as e:
            import errno
            error = errno.errorcode.get(e.errno, '')
            msg = os.strerror(e.errno)
            if error == 'ENOSPC':
                msg = 'Espaço insuficiente para salvar o arquivo.'
            elif error == 'EROFS':
                msg = 'Não é possível salvar arquivos no local especificado.'
            elif error.endswith('NAMETOOLONG'):
                msg = f'O nome do arquivo é grande demais:\n“{e.filename}”.'
            raise TableWritingError(msg, file_name, e)
        except BaseException as e:
            raise TableWritingError(str(e), file_name, e)
    return f


class TableWriter:

    @handle_table_writing_exceptions
    def __init__(self, format, columns, file_name):
        self.file_name = file_name
        self.format = format.upper()
        if format not in ['CSV']:
            raise TableWritingError(f'Formato “{format}” não suportado.',
                                    file_name)
        if format == 'CSV':
            self.fd = open(self.file_name, 'w', newline='',)
            self.writer = csv.DictWriter(
                self.fd,
                columns,
                delimiter=',',
                quoting=csv.QUOTE_NONNUMERIC
            )
        else:
            pass  # possibly add support to more formats later

    def __enter__(self):
        return self

    @handle_table_writing_exceptions
    def __exit__(self, *args):
        if self.fd:
            self.fd.close()

    @handle_table_writing_exceptions
    def write_header(self):
        self.writer.writeheader()

    @handle_table_writing_exceptions
    def write_row(self, row):
        self.writer.writerow(row)
