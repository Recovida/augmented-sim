# coding=utf-8

from typing import Optional, Callable, Any, List, Dict, Union
import csv
import os

from augmented_sim.i18n import get_translator, get_tr


class TableWritingError(Exception):

    def __init__(self, message: str, file_name: str,
                 orig_exception: Optional[BaseException] = None):
        super().__init__(message)
        self.message = message
        self.file_name = file_name
        self.orig_exception = orig_exception
        self.details = ''
        self.trans = get_translator(None)
        self.tr = get_tr('TableWritingError', self.trans)
        if orig_exception:
            import traceback
            tb = traceback.TracebackException.from_exception(orig_exception)
            self.details = ''.join(tb.format())

    def handle_exceptions(self, function: Callable) -> Callable:

        def f(*args, **kwargs) -> Any:
            if hasattr(args[0], 'file_name'):
                self.file_name = args[0].file_name
            else:  # constructor of TableWriter
                self.file_name = args[3]
            try:
                function(*args, **kwargs)
            except FileNotFoundError as e:
                msg = self.tr('invalid-path').format(e.filename)
                raise TableWritingError(msg, e.filename, e)
            except IsADirectoryError as e:
                msg = self.tr('output-file-is-directory').format(e.filename)
                raise TableWritingError(msg, e.filename, e)
            except PermissionError as e:
                msg = self.tr('forbidden')
                raise TableWritingError(msg, e.filename, e)
            except OSError as e:
                import errno
                error = errno.errorcode.get(e.errno, '')
                if error == 'ENOSPC':
                    msg = self.tr('insufficient-space')
                elif error == 'EROFS':
                    msg = self.tr('read-only')
                elif error.endswith('NAMETOOLONG'):
                    msg = self.tr('long-file-name').format(e.filename)
                else:
                    msg = os.strerror(e.errno)
                raise TableWritingError(msg, self.file_name, e)
            except BaseException as e:
                raise TableWritingError(str(e), self.file_name, e)
        return f


handle_table_writing_exceptions = TableWritingError('', '').handle_exceptions


class TableWriter:

    @handle_table_writing_exceptions
    def __init__(self, format: str, columns: List[str], file_name: str):
        self.trans = get_translator(None)
        self.tr = get_tr(type(self).__name__, self.trans)
        self.file_name = file_name
        self.format = format.upper()
        self.fd = None
        self.writer = None
        if format not in ['CSV']:
            msg = self.tr('unsupported-file').format(file_name)
            raise TableWritingError(msg, file_name)
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
    def write_header(self) -> None:
        self.writer.writeheader()

    @handle_table_writing_exceptions
    def write_row(self, row: Dict[str, Union[str, int, float]]) -> None:
        self.writer.writerow(row)
