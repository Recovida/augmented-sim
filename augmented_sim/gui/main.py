# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(890, 367)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setWindowTitle(u"{Nome do Programa}")
        MainWindow.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.edit_outfile1 = QLineEdit(self.centralwidget)
        self.edit_outfile1.setObjectName(u"edit_outfile1")

        self.gridLayout.addWidget(self.edit_outfile1, 2, 2, 1, 2)

        self.label_outfile1 = QLabel(self.centralwidget)
        self.label_outfile1.setObjectName(u"label_outfile1")
        self.label_outfile1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_outfile1, 2, 0, 1, 1)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, -1, 0, -1)
        self.btn_about = QPushButton(self.widget)
        self.btn_about.setObjectName(u"btn_about")
        icon = QIcon()
        iconThemeName = u"help-about"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btn_about.setIcon(icon)

        self.horizontalLayout.addWidget(self.btn_about)

        self.cbox_language = QComboBox(self.widget)
        self.cbox_language.setObjectName(u"cbox_language")

        self.horizontalLayout.addWidget(self.cbox_language)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btn_close = QPushButton(self.widget)
        self.btn_close.setObjectName(u"btn_close")
        icon1 = QIcon()
        iconThemeName = u"exit"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btn_close.setIcon(icon1)

        self.horizontalLayout.addWidget(self.btn_close)


        self.gridLayout.addWidget(self.widget, 11, 0, 1, 5)

        self.label_file1 = QLabel(self.centralwidget)
        self.label_file1.setObjectName(u"label_file1")
        self.label_file1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_file1, 0, 0, 1, 1)

        self.btn_file1 = QPushButton(self.centralwidget)
        self.btn_file1.setObjectName(u"btn_file1")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.btn_file1.sizePolicy().hasHeightForWidth())
        self.btn_file1.setSizePolicy(sizePolicy1)
        self.btn_file1.setMaximumSize(QSize(100, 16777215))
        icon2 = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btn_file1.setIcon(icon2)

        self.gridLayout.addWidget(self.btn_file1, 0, 4, 1, 1)

        self.pbar_current = QProgressBar(self.centralwidget)
        self.pbar_current.setObjectName(u"pbar_current")
        self.pbar_current.setValue(0)

        self.gridLayout.addWidget(self.pbar_current, 7, 2, 1, 3)

        self.label_input_pattern = QLabel(self.centralwidget)
        self.label_input_pattern.setObjectName(u"label_input_pattern")
        self.label_input_pattern.setLayoutDirection(Qt.LeftToRight)
        self.label_input_pattern.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_input_pattern, 1, 0, 1, 1)

        self.label_msg = QLabel(self.centralwidget)
        self.label_msg.setObjectName(u"label_msg")
        sizePolicy.setHeightForWidth(self.label_msg.sizePolicy().hasHeightForWidth())
        self.label_msg.setSizePolicy(sizePolicy)
        self.label_msg.setMinimumSize(QSize(0, 40))
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_msg.setFont(font)
        self.label_msg.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_msg, 4, 0, 1, 5)

        self.pbar_overall = QProgressBar(self.centralwidget)
        self.pbar_overall.setObjectName(u"pbar_overall")
        self.pbar_overall.setValue(0)

        self.gridLayout.addWidget(self.pbar_overall, 5, 2, 1, 3)

        self.list_infile1 = QListWidget(self.centralwidget)
        self.list_infile1.setObjectName(u"list_infile1")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.list_infile1.sizePolicy().hasHeightForWidth())
        self.list_infile1.setSizePolicy(sizePolicy2)
        self.list_infile1.setDragDropMode(QAbstractItemView.InternalMove)

        self.gridLayout.addWidget(self.list_infile1, 0, 2, 1, 2)

        self.label_current_file = QLabel(self.centralwidget)
        self.label_current_file.setObjectName(u"label_current_file")
        self.label_current_file.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_current_file, 10, 2, 1, 3)

        self.label_current_progress = QLabel(self.centralwidget)
        self.label_current_progress.setObjectName(u"label_current_progress")
        self.label_current_progress.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_current_progress, 7, 0, 1, 1)

        self.btn_outfile1 = QPushButton(self.centralwidget)
        self.btn_outfile1.setObjectName(u"btn_outfile1")
        sizePolicy1.setHeightForWidth(self.btn_outfile1.sizePolicy().hasHeightForWidth())
        self.btn_outfile1.setSizePolicy(sizePolicy1)
        self.btn_outfile1.setMaximumSize(QSize(100, 16777215))
        icon3 = QIcon()
        iconThemeName = u"document-export"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.btn_outfile1.setIcon(icon3)

        self.gridLayout.addWidget(self.btn_outfile1, 2, 4, 1, 1)

        self.label_overall_progress = QLabel(self.centralwidget)
        self.label_overall_progress.setObjectName(u"label_overall_progress")
        self.label_overall_progress.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_overall_progress, 5, 0, 1, 1)

        self.btn_execute = QPushButton(self.centralwidget)
        self.btn_execute.setObjectName(u"btn_execute")
        self.btn_execute.setFont(font)

        self.gridLayout.addWidget(self.btn_execute, 3, 2, 1, 3)

        self.cbox_input_pattern = QComboBox(self.centralwidget)
        self.cbox_input_pattern.setObjectName(u"cbox_input_pattern")

        self.gridLayout.addWidget(self.cbox_input_pattern, 1, 2, 1, 3)

        self.gridLayout.setRowStretch(0, 4)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(2, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.btn_close.clicked.connect(MainWindow.close)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.label_outfile1.setText(QCoreApplication.translate("MainWindow", u"output-file", None))
        self.btn_about.setText(QCoreApplication.translate("MainWindow", u"about", None))
        self.btn_close.setText(QCoreApplication.translate("MainWindow", u"exit", None))
        self.label_file1.setText(QCoreApplication.translate("MainWindow", u"input-files", None))
        self.btn_file1.setText(QCoreApplication.translate("MainWindow", u"add", None))
        self.label_input_pattern.setText(QCoreApplication.translate("MainWindow", u"input-pattern", None))
        self.label_msg.setText("")
        self.label_current_file.setText("")
        self.label_current_progress.setText(QCoreApplication.translate("MainWindow", u"current-progress", None))
        self.btn_outfile1.setText(QCoreApplication.translate("MainWindow", u"choose", None))
        self.label_overall_progress.setText(QCoreApplication.translate("MainWindow", u"overall-progress", None))
        self.btn_execute.setText(QCoreApplication.translate("MainWindow", u"generate", None))
        pass
    # retranslateUi

