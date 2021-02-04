#!/usr/bin/env python3
# coding=utf-8

import argparse
import os.path
import pathlib
import sys

from typing import Type, Optional, List, Tuple

from PySide2.QtGui import QKeyEvent, QKeySequence
from PySide2.QtCore import QObject, Signal, QRect, QEvent
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QMessageBox, QDialog, QDialogButtonBox, QWidget, \
    QVBoxLayout, QScrollArea, QTextBrowser, QFrame


if vars(sys.modules[__name__])['__package__'] is None and \
        __name__ == '__main__':
    # allow running from any folder
    here = pathlib.Path(__file__).parent.parent.resolve()
    sys.path.insert(1, str(here))


from augmented_sim.core import AugmentedSIM
from augmented_sim.gui.main import Ui_MainWindow
from augmented_sim.gui.about import Ui_AboutDialog
from augmented_sim.i18n import get_translator, get_tr, \
    AVAILABLE_LANGUAGES, CHOSEN_LANGUAGE, change_language_globally
from augmented_sim import PROGRAM_METADATA

from augmented_sim.sim.input_pattern import ALL_PATTERNS


class DeleteFilter(QObject):

    def eventFilter(self, o: QWidget, e: QEvent) -> bool:
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

    def __init__(self, augment_cls: Type,
                 input_files: Optional[List[str]] = None,
                 output_file: Optional[str] = None,
                 pattern_name: Optional[str] = ''):
        super().__init__()
        self.augment_cls = augment_cls

        self.app = QApplication(sys.argv)

        self.trans = get_translator(None)
        self.tr = get_tr(type(self).__name__, self.trans)
        self.app.installTranslator(self.trans)

        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.setWindowTitle(PROGRAM_METADATA.get('NAME', 'x'))
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
        for code, name, *_ in AVAILABLE_LANGUAGES:
            self.ui.cbox_language.addItem(name, code)
        self.ui.cbox_input_pattern.addItem('', '')
        self.ui.cbox_language.setCurrentIndex(
            self.ui.cbox_language.findData(CHOSEN_LANGUAGE))
        for p in ALL_PATTERNS:
            self.ui.cbox_input_pattern.addItem(p, p)
        self.ui.cbox_input_pattern.setCurrentIndex(
            self.ui.cbox_input_pattern.findData(pattern_name))
        self.ui.cbox_language.currentIndexChanged.connect(
            lambda idx:
            self.change_language(self.ui.cbox_language.itemData(idx)))
        self.widgets_to_disable = [
            self.ui.btn_execute, self.ui.btn_file1, self.ui.btn_outfile1,
            self.ui.list_infile1, self.ui.edit_outfile1, self.ui.btn_close,
            self.ui.cbox_input_pattern
        ]
        if input_files:
            self.fill_file1(input_files)
        if output_file:
            self.fill_outfile1(output_file)
        self.hide_progress()
        self.window.show()
        self.app.exec_()

    def show_about(self) -> None:
        # show window
        w = QDialog(self.window)
        name = PROGRAM_METADATA.get('NAME', '')
        version = PROGRAM_METADATA.get('VERSION', '')
        year = PROGRAM_METADATA.get('YEAR', '')
        ui = Ui_AboutDialog()
        ui.setupUi(w)
        w.setWindowTitle(self.tr('about-program').format(name))
        ui.label_name.setText(name)
        ui.label_version.setText(f'{version} ({year})')
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
        ui.buttonBox.button(QDialogButtonBox.Close).setText(
            self.tr('close'))
        w.exec_()

    def change_language(self, language: str) -> None:
        change_language_globally(language)
        self.trans = get_translator(None)
        self.tr = get_tr(type(self).__name__, self.trans)
        self.app.installTranslator(self.trans)
        self.ui.retranslateUi(self.window)

    def choose_file1(self) -> None:
        options = QFileDialog.Options()
        names, _ = QFileDialog.getOpenFileNames(
            self.window, self.tr('input-files'), '',
            'DBase File / Comma-Separated Values (*.dbf *.csv)',
            options=options
        )
        self.fill_file1(names)

    def fill_file1(self, files: List[str]) -> None:
        w = self.ui.list_infile1
        existing = {w.item(i).text() for i in range(w.count())}
        for f in files:
            if f not in existing and os.path.isfile(f):
                f = os.path.abspath(f)
                self.ui.list_infile1.addItem(f)
                existing.add(f)

    def choose_outfile1(self) -> None:
        options = QFileDialog.Options()
        f, _ = QFileDialog.getSaveFileName(
            self.window, self.tr('output-file'), '',
            'Comma-Separated Values (*.csv)',
            options=options
        )
        if f:
            if not f.lower().endswith('.csv'):
                f += '.csv'
            self.fill_outfile1(f)

    def fill_outfile1(self, file: Optional[str]) -> None:
        if file and os.path.isdir(os.path.dirname(file)):
            self.ui.edit_outfile1.setText(os.path.abspath(file))

    def _error_msg(self, title: str, message: str, details: str = '') -> None:
        msgbox = QMessageBox(
            QMessageBox.Critical,
            title, message,
            buttons=QMessageBox.Ok,
            parent=self.window
        )
        msgbox.setDetailedText(details)
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.exec_()

    def execute(self) -> None:
        w = self.ui.list_infile1
        input_files = [w.item(i).text() for i in range(w.count())]
        output_file = self.ui.edit_outfile1.text()
        pattern_name = self.ui.cbox_input_pattern.currentData()
        self.current_progress_signal.emit(0)
        self.overall_progress_signal.emit(0)
        self.current_file_signal.emit('')
        if not (input_files and output_file):
            self.ui.label_msg.setText('')
            self._error_msg(self.tr('error'),
                            self.tr('missing-files'))
            return
        if output_file in input_files:
            self.ui.label_msg.setText('')
            self._error_msg(self.tr('error'),
                            self.tr('output-cannot-be-input'))
            return
        if not pattern_name:
            self.ui.label_msg.setText('')
            self._error_msg(self.tr('error'),
                            self.tr('blank-pattern'))
            return
        self.show_progress()
        aug = self.augment_cls(input_files, output_file, pattern_name)
        self.disable_widgets()
        self.ui.label_msg.setText(self.tr('executing'))
        self.ui.label_msg.repaint()
        aug.augment(
            report_progress=self.update_progress,
            report_exception=self.on_error
        )

    def on_error(self, e: BaseException) -> None:
        msg = getattr(e, 'message', str(e))
        details = getattr(e, 'details', '')
        self.status_msg_signal.emit('')
        self.current_file_signal.emit('')
        self.current_progress_signal.emit(0)
        self.overall_progress_signal.emit(0)
        self.error_signal.emit(self.tr('error'), msg, details)
        self.enable_widgets()
        self.hide_progress()

    def enable_widgets(self, enable: bool = True) -> None:
        for w in self.widgets_to_disable:
            w.setEnabled(enable)

    def disable_widgets(self) -> None:
        self.enable_widgets(False)

    def update_progress(self, p: Tuple[int, int, int, int, Optional[str]]) \
            -> None:
        self.current_progress_signal.emit(int((100 * p[0]) / p[1]))
        self.overall_progress_signal.emit(int((100 * p[2]) / p[3]))
        self.current_file_signal.emit(p[-1] or '')
        if p[2] == p[3]:
            self.ui.label_msg.setText(self.tr('file-saved'))
            self.enable_widgets()
            self.current_file_signal.emit('')

    def show_progress(self, show: bool = True) -> None:
        widgets = [self.ui.pbar_overall,
                   self.ui.pbar_current,
                   self.ui.label_overall_progress,
                   self.ui.label_current_progress]
        for w in widgets:
            w.setVisible(show)

    def hide_progress(self) -> None:
        self.show_progress(False)


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('output_file', nargs='?',
                            help='output file name (CSV)')
    arg_parser.add_argument('input_files', nargs='*',
                            help='input file names (DBF or CSV)')
    arg_parser.add_argument('--pattern', '-p', type=str, default='')
    a = arg_parser.parse_args()
    AugmentedSIMGUI(
        augment_cls=AugmentedSIM,
        input_files=a.input_files,
        output_file=a.output_file,
        pattern_name=a.pattern,
    )


if __name__ == '__main__':
    main()
