# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.setWindowModality(Qt.WindowModal)
        AboutDialog.resize(472, 421)
        AboutDialog.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
        AboutDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(AboutDialog)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame = QFrame(self.widget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout.addWidget(self.frame)

        self.widget_4 = QWidget(self.widget)
        self.widget_4.setObjectName(u"widget_4")
        self.verticalLayout_2 = QVBoxLayout(self.widget_4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.widget_4)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)

        self.label_version = QLabel(self.widget_4)
        self.label_version.setObjectName(u"label_version")
        self.label_version.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_version)


        self.horizontalLayout.addWidget(self.widget_4)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 12)

        self.verticalLayout.addWidget(self.widget)

        self.tabWidget = QTabWidget(AboutDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_3 = QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_descr = QLabel(self.tab)
        self.label_descr.setObjectName(u"label_descr")

        self.verticalLayout_3.addWidget(self.label_descr)

        self.label_help_link = QLabel(self.tab)
        self.label_help_link.setObjectName(u"label_help_link")

        self.verticalLayout_3.addWidget(self.label_help_link)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_5 = QVBoxLayout(self.tab_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_project = QLabel(self.tab_3)
        self.label_project.setObjectName(u"label_project")

        self.verticalLayout_5.addWidget(self.label_project)

        self.label_index_link = QLabel(self.tab_3)
        self.label_index_link.setObjectName(u"label_index_link")

        self.verticalLayout_5.addWidget(self.label_index_link)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tabWidget_2 = QTabWidget(self.tab_2)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.tabWidget_2.addTab(self.tab_4, "")

        self.verticalLayout_4.addWidget(self.tabWidget_2)

        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)
        self.buttonBox.rejected.connect(AboutDialog.close)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"Sobre Augmented SIM", None))
        self.label.setText(QCoreApplication.translate("AboutDialog", u"Augmented SIM", None))
        self.label_version.setText(QCoreApplication.translate("AboutDialog", u"v0.0.0 (0000)", None))
        self.label_descr.setText(QCoreApplication.translate("AboutDialog", u"{BREVE DESCRI\u00c7\u00c3O DO PROGRAMA AQUI}", None))
        self.label_help_link.setText(QCoreApplication.translate("AboutDialog", u"{LINK PARA DOCUMENTA\u00c7\u00c3O}", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("AboutDialog", u"Programa", None))
        self.label_project.setText(QCoreApplication.translate("AboutDialog", u"{INFORMA\u00c7\u00c3O SOBRE PROJETO AQUI}", None))
        self.label_index_link.setText(QCoreApplication.translate("AboutDialog", u"{LINK PARA REPOSIT\u00d3RIO-\u00cdNDICE}", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("AboutDialog", u"Desenvolvimento", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), QCoreApplication.translate("AboutDialog", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("AboutDialog", u"Frameworks, bibliotecas e licen\u00e7as", None))
    # retranslateUi

