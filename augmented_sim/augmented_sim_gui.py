#!/usr/bin/env python3
# coding=utf-8

import argparse
import os.path
import sys

from PyQt5.QtGui import QKeyEvent, QKeySequence
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, \
                            QMessageBox


if vars(sys.modules[__name__])['__package__'] is None and \
                                                    __name__ == '__main__':
    # allow running from any folder
    import pathlib
    here = pathlib.Path(__file__).parent.parent.resolve()
    sys.path.insert(1, str(here))


from augmented_sim.gui.gui import Ui_MainWindow
from augmented_sim.core import AugmentedSIM


class DeleteFilter(QObject):

    def eventFilter(self, o, e):
        if isinstance(e, QKeyEvent) and e.type() == QKeyEvent.KeyPress \
                and e.matches(QKeySequence.Delete):
            idx = o.currentRow()
            if idx >= 0:
                o.takeItem(idx)
            return True
        return super().eventFilter(o, e)


class AugmentedSIMGUI(QObject):

    overall_progress_signal = pyqtSignal(int)
    current_progress_signal = pyqtSignal(int)
    current_file_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str, str)
    status_msg_signal = pyqtSignal(str)

    def __init__(self, augment_cls, input_files=None, output_file=None):
        super().__init__()
        self.augment_cls = augment_cls
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.ui.btn_file1.clicked.connect(lambda *a: self.choose_file1())
        self.ui.btn_outfile1.clicked.connect(lambda *a: self.choose_outfile1())
        self.ui.btn_execute.clicked.connect(lambda *a: self.execute())
        self.overall_progress_signal.connect(self.ui.pbar_overall.setValue)
        self.current_progress_signal.connect(self.ui.pbar_current.setValue)
        self.current_file_signal.connect(self.ui.label_current_file.setText)
        self.status_msg_signal.connect(self.ui.label_msg.setText)
        self.error_signal.connect(self._error_msg)
        self.df = DeleteFilter()
        self.ui.list_infile1.installEventFilter(self.df)
        self.widgets_to_disable = [
            self.ui.btn_execute, self.ui.btn_file1, self.ui.btn_outfile1,
            self.ui.list_infile1, self.ui.edit_outfile1
        ]
        if input_files:
            self.fill_file1(input_files)
        if output_file:
            self.fill_outfile1(output_file)
        self.window.show()
        self.app.exec_()

    def choose_file1(self):
        options = QFileDialog.Options()
        names, _ = QFileDialog.getOpenFileNames(
            self.window, 'Arquivo de entrada 1', '',
            'DBase File or Comma-Separated Values (*.dbf *.csv)',
            options=options
        )
        self.fill_file1(names)

    def fill_file1(self, files):
        w = self.ui.list_infile1
        existing = {w.item(i).text() for i in range(w.count())}
        for f in files:
            if f not in existing and os.path.isfile(f):
                f = os.path.abspath(f)
                self.ui.list_infile1.addItem(f)
                existing.add(f)

    def choose_outfile1(self):
        options = QFileDialog.Options()
        f, _ = QFileDialog.getSaveFileName(
            self.window, 'Arquivo de saída', '',
            'Comma-Separated Values (*.csv)',
            options=options
        )
        if f:
            if not f.lower().endswith('.csv'):
                f += '.csv'
            self.fill_outfile1(f)

    def fill_outfile1(self, file):
        if file and os.path.isdir(os.path.dirname(file)):
            self.ui.edit_outfile1.setText(os.path.abspath(file))

    def _error_msg(self, title, message):
        msgbox = QMessageBox(
            QMessageBox.Critical,
            title, message,
            buttons=QMessageBox.Ok,
            parent=self.window
        )
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.exec_()

    def execute(self):
        w = self.ui.list_infile1
        input_files = [w.item(i).text() for i in range(w.count())]
        output_file = self.ui.edit_outfile1.text()
        self.current_progress_signal.emit(0)
        self.overall_progress_signal.emit(0)
        self.current_file_signal.emit('')
        if not (input_files and output_file):
            self.ui.label_msg.setText('')
            self._error_msg('Erro',
                            'Escolha os arquivos e clique em Executar.')
            return
        if output_file in input_files:
            self.ui.label_msg.setText('')
            self._error_msg('Erro',
                            'O arquivo de saída não pode ser um dos '
                            'arquivos de entrada.')
            return
        aug = self.augment_cls(input_files, output_file)
        self.disable_widgets()
        self.ui.label_msg.setText('Executando operação…')
        self.ui.label_msg.repaint()
        aug.augment(
            report_progress=self.update_progress,
            report_exception=self.on_error
        )

    def on_error(self, e, msg):
        self.status_msg_signal.emit('')
        self.error_signal.emit('Erro', msg)
        self.enable_widgets()

    def enable_widgets(self, enable=True):
        for w in self.widgets_to_disable:
            w.setEnabled(enable)

    def disable_widgets(self):
        self.enable_widgets(False)

    def update_progress(self, progress):
        self.current_progress_signal.emit(int((100*progress[0]) / progress[1]))
        self.overall_progress_signal.emit(int((100*progress[2]) / progress[3]))
        self.current_file_signal.emit(progress[-1] or '')
        if progress[2] == progress[3]:
            self.ui.label_msg.setText('O arquivo foi salvo.')
            self.enable_widgets()
            self.current_file_signal.emit('')


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('output_file', nargs='?',
                            help='output file name (CSV)')
    arg_parser.add_argument('input_files', nargs='*',
                            help='input file names (DBF or CSV)')
    a = arg_parser.parse_args()
    AugmentedSIMGUI(
        augment_cls=AugmentedSIM,
        input_files=a.input_files,
        output_file=a.output_file,
    )


if __name__ == '__main__':
    main()
