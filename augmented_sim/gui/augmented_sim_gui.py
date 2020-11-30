#!/usr/bin/env python3

try:
    from PyQt5.QtCore import QObject
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

    from .gui import Ui_MainWindow
except Exception as e:
    print('PyQt5 não foi encontrado. Segue traceback:')
    raise e

import sys


class AugmentedSIMGUI(QObject):

    def __init__(self, augment_cls):
        super().__init__()
        self.augment_cls = augment_cls
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.ui.btn_file1.clicked.connect(lambda *a: self.choose_file1())
        self.ui.btn_outfile1.clicked.connect(lambda *a: self.choose_outfile1())
        self.ui.btn_execute.clicked.connect(lambda *a: self.execute())
        self.window.show()
        self.app.exec_()

    def choose_file1(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        f, _ = QFileDialog.getOpenFileName(
            self.window, 'Arquivo de entrada 1', '',
            'DBase File or Comma-Separated Values (*.dbf *.csv)',
            options=options
        )
        if f:
            self.ui.edit_file1.setText(f)
            # generate output file name
            output_f = f.rsplit('.', 1)[0] + '_expanded.csv'
            self.ui.edit_outfile1.setText(output_f)

    def choose_outfile1(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        f, _ = QFileDialog.getSaveFileName(
            self.window, 'Arquivo de saída', '',
            'Comma-Separated Values (*.csv)',
            options=options
        )
        if f:
            self.ui.edit_outfile1.setText(f)

    def execute(self):
        input_file = self.ui.edit_file1.text()
        output_file = self.ui.edit_outfile1.text()
        if not (input_file and output_file):
            self.ui.label_msg.setText(
                'Escolha os arquivos e clique em Executar.'
            )
        aug = self.augment_cls(input_file, output_file)
        try:
            self.ui.label_msg.setText('Executando operação…')
            aug.augment()
        except Exception:
            import traceback
            self.ui.label_msg.setText(
                'Houve um erro: \n' + traceback.format_exc()
            )
        else:
            self.ui.label_msg.setText('O arquivo foi salvo.')


if __name__ == '__main__':
    AugmentedSIMGUI()
