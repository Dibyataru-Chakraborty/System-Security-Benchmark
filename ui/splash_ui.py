# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'splash_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QProgressBar, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Splash(object):
    def setupUi(self, Splash):
        if not Splash.objectName():
            Splash.setObjectName(u"Splash")
        Splash.resize(848, 392)
        Splash.setCursor(QCursor(Qt.CursorShape.BlankCursor))
        Splash.setStyleSheet(u"QWidget#Splash {\n"
"    background-color: #FFFFFF;\n"
"    border: 2px solid #800000;\n"
"    border-radius: 12px;\n"
"}")
        self.gridLayout = QGridLayout(Splash)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(270, 22, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.welcome = QLabel(Splash)
        self.welcome.setObjectName(u"welcome")
        self.welcome.setStyleSheet(u"font-family: 'Segoe UI', -apple-system, sans-serif;\n"
"font-size: 32pt;\n"
"font-weight: bold;\n"
"color: #800000;\n"
"background-color: transparent;\n"
"border: none;")

        self.horizontalLayout.addWidget(self.welcome)

        self.horizontalSpacer = QSpacerItem(21, 38, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.progressBar = QProgressBar(Splash)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"    border: 1px solid #E2DADA;\n"
"    border-radius: 8px;\n"
"    background-color: #FAF5F5;\n"
"    text-align: center;\n"
"    color: #1E293B;\n"
"    font-weight: bold;\n"
"    font-size: 14px;\n"
"    height: 24px;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #800000;\n"
"    border-radius: 8px;\n"
"}")
        self.progressBar.setValue(24)

        self.verticalLayout.addWidget(self.progressBar)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(Splash)

        QMetaObject.connectSlotsByName(Splash)
    # setupUi

    def retranslateUi(self, Splash):
        Splash.setWindowTitle(QCoreApplication.translate("Splash", u"Form", None))
        self.welcome.setText(QCoreApplication.translate("Splash", u"<html><head/><body><p align=\"center\">Digi Samurai</p></body></html>", None))
    # retranslateUi

