#!/usr/bin/env python3
# coding=utf-8

import argparse
import os.path
import sys

from PySide2.QtGui import QKeyEvent, QKeySequence
from PySide2.QtCore import QObject, Signal, QRect
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, \
                            QMessageBox, QDialog, QDialogButtonBox, QWidget, \
                            QVBoxLayout, QScrollArea, QTextBrowser, QFrame


if vars(sys.modules[__name__])['__package__'] is None and \
                                                    __name__ == '__main__':
    # allow running from any folder
    import pathlib
    here = pathlib.Path(__file__).parent.parent.resolve()
    sys.path.insert(1, str(here))


from augmented_sim.gui.main import Ui_MainWindow
from augmented_sim.gui.about import Ui_AboutDialog
from augmented_sim.core import AugmentedSIM
from augmented_sim import PROGRAM_METADATA


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

    overall_progress_signal = Signal(int)
    current_progress_signal = Signal(int)
    current_file_signal = Signal(str)
    error_signal = Signal(str, str, str)
    status_msg_signal = Signal(str)

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
        self.ui.btn_about.clicked.connect(lambda *a: self.show_about())
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
        self.hide_progress()
        self.window.show()
        self.app.exec_()

    def show_about(self):
        # show window
        w = QDialog(self.window)
        ui = Ui_AboutDialog()
        ui.setupUi(w)
        ui.text_browser_licence.setMarkdown(
            PROGRAM_METADATA.get('LICENCE_TEXT', '')
        )
        ui.text_browser_read_me.setMarkdown(
            PROGRAM_METADATA.get('READ_ME', '')
        )
        ui.text_browser_project.setMarkdown(
            PROGRAM_METADATA.get('PROJECT_DESCRIPTION', '')
        )
        ui.tabs = []
        while ui.tabs_external_licences.count():
            ui.tabs_external_licences.removeTab(0)
        for name, contents in PROGRAM_METADATA.get('LICENCES', []):
            tab = QWidget()
            sa = QScrollArea(tab)
            vl1 = QVBoxLayout(tab)
            sa.setWidgetResizable(True)
            sac = QWidget()
            sac.setGeometry(QRect(0, 0, 492, 262))
            vl2 = QVBoxLayout(sac)
            text_browser = QTextBrowser(sac)
            text_browser.setMarkdown(contents)
            text_browser.setFrameShape(QFrame.NoFrame)
            vl2.addWidget(text_browser)
            sa.setWidget(sac)
            vl1.addWidget(sa)
            vl1.setContentsMargins(0, 0, 0, 0)
            vl2.setContentsMargins(0, 0, 0, 0)
            ui.tabs_external_licences.addTab(tab, name)
            ui.tabs.append((tab, vl1, sa, sac, vl1, vl2, text_browser))
        ui.buttonBox.button(QDialogButtonBox.Close).setText('Fechar')
        w.exec_()

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

    def _error_msg(self, title, message, details=''):
        msgbox = QMessageBox(
            QMessageBox.Critical,
            title, message,
            buttons=QMessageBox.Ok,
            parent=self.window
        )
        msgbox.setDetailedText(details)
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
                            'Escolha os arquivos de entrada '
                            'e o arquivo de saída.')
            return
        if output_file in input_files:
            self.ui.label_msg.setText('')
            self._error_msg('Erro',
                            'O arquivo de saída não pode ser um dos '
                            'arquivos de entrada.')
            return
        self.show_progress()
        aug = self.augment_cls(input_files, output_file)
        self.disable_widgets()
        self.ui.label_msg.setText('Executando operação…')
        self.ui.label_msg.repaint()
        aug.augment(
            report_progress=self.update_progress,
            report_exception=self.on_error
        )

    def on_error(self, e):
        msg = getattr(e, 'message', str(e))
        details = getattr(e, 'details', '')
        self.status_msg_signal.emit('')
        self.current_file_signal.emit('')
        self.current_progress_signal.emit(0)
        self.overall_progress_signal.emit(0)
        self.error_signal.emit('Erro', msg, details)
        self.enable_widgets()
        self.hide_progress()

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

    def show_progress(self, show=True):
        widgets = [self.ui.pbar_overall,
                   self.ui.pbar_current,
                   self.ui.label_overall_progress,
                   self.ui.label_current_progress]
        for w in widgets:
            w.setVisible(show)

    def hide_progress(self):
        self.show_progress(False)


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
