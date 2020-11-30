# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(871, 313)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.edit_file2 = QtWidgets.QLineEdit(self.centralwidget)
        self.edit_file2.setObjectName("edit_file2")
        self.gridLayout.addWidget(self.edit_file2, 1, 3, 1, 1)
        self.btn_file1 = QtWidgets.QPushButton(self.centralwidget)
        self.btn_file1.setObjectName("btn_file1")
        self.gridLayout.addWidget(self.btn_file1, 0, 4, 1, 1)
        self.btn_file2 = QtWidgets.QPushButton(self.centralwidget)
        self.btn_file2.setObjectName("btn_file2")
        self.gridLayout.addWidget(self.btn_file2, 1, 4, 1, 1)
        self.btn_execute = QtWidgets.QPushButton(self.centralwidget)
        self.btn_execute.setObjectName("btn_execute")
        self.gridLayout.addWidget(self.btn_execute, 4, 0, 1, 5)
        self.label_file1 = QtWidgets.QLabel(self.centralwidget)
        self.label_file1.setObjectName("label_file1")
        self.gridLayout.addWidget(self.label_file1, 0, 0, 1, 1)
        self.label_file2 = QtWidgets.QLabel(self.centralwidget)
        self.label_file2.setObjectName("label_file2")
        self.gridLayout.addWidget(self.label_file2, 1, 0, 1, 1)
        self.edit_file1 = QtWidgets.QLineEdit(self.centralwidget)
        self.edit_file1.setObjectName("edit_file1")
        self.gridLayout.addWidget(self.edit_file1, 0, 3, 1, 1)
        self.label_msg = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_msg.sizePolicy().hasHeightForWidth())
        self.label_msg.setSizePolicy(sizePolicy)
        self.label_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.label_msg.setObjectName("label_msg")
        self.gridLayout.addWidget(self.label_msg, 5, 0, 1, 5)
        self.edit_outfile1 = QtWidgets.QLineEdit(self.centralwidget)
        self.edit_outfile1.setObjectName("edit_outfile1")
        self.gridLayout.addWidget(self.edit_outfile1, 3, 3, 1, 1)
        self.btn_outfile1 = QtWidgets.QPushButton(self.centralwidget)
        self.btn_outfile1.setObjectName("btn_outfile1")
        self.gridLayout.addWidget(self.btn_outfile1, 3, 4, 1, 1)
        self.label_outfile1 = QtWidgets.QLabel(self.centralwidget)
        self.label_outfile1.setObjectName("label_outfile1")
        self.gridLayout.addWidget(self.label_outfile1, 3, 0, 1, 1)
        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 2)
        self.gridLayout.setRowStretch(2, 1)
        self.gridLayout.setRowStretch(3, 2)
        self.gridLayout.setRowStretch(4, 2)
        self.gridLayout.setRowStretch(5, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_file1.setText(_translate("MainWindow", "Escolher..."))
        self.btn_file2.setText(_translate("MainWindow", "Escolher..."))
        self.btn_execute.setText(_translate("MainWindow", "Executar operação"))
        self.label_file1.setText(_translate("MainWindow", "Arquivo de entrada 1"))
        self.label_file2.setText(_translate("MainWindow", "Arquivo de entrada 2"))
        self.label_msg.setText(_translate("MainWindow", "Alguma informação sobre progresso, erro, etc. aqui"))
        self.btn_outfile1.setText(_translate("MainWindow", "Escolher..."))
        self.label_outfile1.setText(_translate("MainWindow", "Arquivo de saída 1"))
