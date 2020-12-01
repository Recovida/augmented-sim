#!/usr/bin/env python3

try:
    from PyQt5.QtGui import QKeyEvent, QKeySequence
    from PyQt5.QtCore import QObject, pyqtSignal
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

    from .gui import Ui_MainWindow
except Exception as e:
    print('PyQt5 não foi encontrado. Segue traceback:')
    raise e

import sys


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

    overall_progress_signal = pyqtSignal(float)
    current_progress_signal = pyqtSignal(float)
    current_file_signal = pyqtSignal(str)

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
        self.overall_progress_signal.connect(self.ui.pbar_overall.setValue)
        self.current_progress_signal.connect(self.ui.pbar_current.setValue)
        self.current_file_signal.connect(self.ui.label_current_file.setText)
        self.df = DeleteFilter()
        self.ui.list_infile1.installEventFilter(self.df)
        self.widgets_to_disable = [
            self.ui.btn_execute, self.ui.btn_file1, self.ui.btn_outfile1,
            self.ui.list_infile1, self.ui.edit_outfile1
        ]
        self.window.show()
        self.app.exec_()

    def choose_file1(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        names, _ = QFileDialog.getOpenFileNames(
            self.window, 'Arquivo de entrada 1', '',
            'DBase File or Comma-Separated Values (*.dbf *.csv)',
            options=options
        )
        for f in names:
            self.ui.list_infile1.addItem(f)

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
        w = self.ui.list_infile1
        input_files = [w.item(i).text() for i in range(w.count())]
        output_file = self.ui.edit_outfile1.text()
        self.current_progress_signal.emit(0)
        self.overall_progress_signal.emit(0)
        self.current_file_signal.emit('')
        if not (input_files and output_file):
            self.ui.label_msg.setText(
                'Escolha os arquivos e clique em Executar.'
            )
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
        self.ui.label_msg.setText(
            'Houve um erro: \n' + msg
        )
        self.enable_widgets()

    def enable_widgets(self, enable=True):
        for w in self.widgets_to_disable:
            w.setEnabled(enable)

    def disable_widgets(self):
        self.enable_widgets(False)

    def update_progress(self, progress):
        self.current_progress_signal.emit((100 * progress[0]) // progress[1])
        self.overall_progress_signal.emit((100 * progress[2]) // progress[3])
        self.current_file_signal.emit(progress[-1] or '')
        if progress[2] == progress[3]:
            self.ui.label_msg.setText('O arquivo foi salvo.')
            self.enable_widgets()
            self.current_file_signal.emit('')


if __name__ == '__main__':
    AugmentedSIMGUI()
