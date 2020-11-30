#!/usr/bin/env python3

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from gui import Ui_MainWindow
import sys


class Example(QObject):

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.ui.btn_file1.clicked.connect(lambda *a: self.choose_file1())
        self.ui.btn_file2.clicked.connect(lambda *a: self.choose_file2())
        self.ui.btn_outfile1.clicked.connect(lambda *a: self.choose_outfile1())
        self.window.show()
        self.app.exec_()

    def choose_file1(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        f, _ = QFileDialog.getOpenFileName(
            self.window, 'Arquivo de entrada 1', '',
            'Qualquer extensão (*.*)', options=options
        )
        if f:
            self.ui.edit_file1.setText(f)

    def choose_file2(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        f, _ = QFileDialog.getOpenFileName(
            self.window, 'Arquivo de entrada 2', '',
            'Qualquer extensão (*.*)', options=options
        )
        if f:
            self.ui.edit_file2.setText(f)

    def choose_outfile1(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        f, _ = QFileDialog.getSaveFileName(
            self.window, 'Arquivo de saída 1', '',
            'Qualquer extensão (*.*)', options=options
        )
        if f:
            self.ui.edit_outfile1.setText(f)


if __name__ == '__main__':
    Example()
