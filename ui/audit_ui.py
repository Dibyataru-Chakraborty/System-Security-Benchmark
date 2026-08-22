# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'audit_ui.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGridLayout,
    QHBoxLayout, QHeaderView, QLineEdit, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QSplitter,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_Zero_Security(object):
    def setupUi(self, Zero_Security):
        if not Zero_Security.objectName():
            Zero_Security.setObjectName(u"Zero_Security")
        Zero_Security.resize(1132, 842)
        Zero_Security.setAutoFillBackground(True)
        self.gridLayout_4 = QGridLayout(Zero_Security)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.source_layout = QHBoxLayout()
        self.source_layout.setObjectName(u"source_layout")
        self.radio_local = QRadioButton(Zero_Security)
        self.radio_local.setObjectName(u"radio_local")
        self.radio_local.setChecked(True)

        self.source_layout.addWidget(self.radio_local)

        self.radio_online = QRadioButton(Zero_Security)
        self.radio_online.setObjectName(u"radio_online")

        self.source_layout.addWidget(self.radio_online)


        self.verticalLayout_2.addLayout(self.source_layout)

        self.tech_dropdown = QComboBox(Zero_Security)
        self.tech_dropdown.setObjectName(u"tech_dropdown")

        self.verticalLayout_2.addWidget(self.tech_dropdown)

        self.benchmark_dropdown = QComboBox(Zero_Security)
        self.benchmark_dropdown.setObjectName(u"benchmark_dropdown")

        self.verticalLayout_2.addWidget(self.benchmark_dropdown)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.path = QLineEdit(Zero_Security)
        self.path.setObjectName(u"path")

        self.horizontalLayout_3.addWidget(self.path)

        self.browse = QPushButton(Zero_Security)
        self.browse.setObjectName(u"browse")

        self.horizontalLayout_3.addWidget(self.browse)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.dropbox = QComboBox(Zero_Security)
        self.dropbox.addItem("")
        self.dropbox.addItem("")
        self.dropbox.addItem("")
        self.dropbox.addItem("")
        self.dropbox.addItem("")
        self.dropbox.addItem("")
        self.dropbox.setObjectName(u"dropbox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dropbox.sizePolicy().hasHeightForWidth())
        self.dropbox.setSizePolicy(sizePolicy)
        self.dropbox.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_2.addWidget(self.dropbox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.cancel = QPushButton(Zero_Security)
        self.cancel.setObjectName(u"cancel")

        self.horizontalLayout.addWidget(self.cancel)

        self.submit = QPushButton(Zero_Security)
        self.submit.setObjectName(u"submit")

        self.horizontalLayout.addWidget(self.submit)

        self.backup_btn = QPushButton(Zero_Security)
        self.backup_btn.setObjectName(u"backup_btn")

        self.horizontalLayout.addWidget(self.backup_btn)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(Zero_Security)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.path_table = QTableWidget(self.widget)
        if (self.path_table.columnCount() < 1):
            self.path_table.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.path_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        self.path_table.setObjectName(u"path_table")
        self.path_table.setMouseTracking(True)
        self.path_table.setAutoFillBackground(True)
        self.path_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.path_table.setTabKeyNavigation(True)
        self.path_table.setProperty(u"showDropIndicator", False)
        self.path_table.setDragDropOverwriteMode(False)
        self.path_table.setAlternatingRowColors(True)
        self.path_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.path_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.path_table.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.path_table)

        self.dashboard_plot = QTabWidget(self.widget)
        self.dashboard_plot.setObjectName(u"dashboard_plot")
        self.ax1 = QWidget()
        self.ax1.setObjectName(u"ax1")
        self.gridLayout_5 = QGridLayout(self.ax1)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.dashboard_plot.addTab(self.ax1, "")
        self.ax2 = QWidget()
        self.ax2.setObjectName(u"ax2")
        self.gridLayout_3 = QGridLayout(self.ax2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.dashboard_plot.addTab(self.ax2, "")
        self.ax3 = QWidget()
        self.ax3.setObjectName(u"ax3")
        self.gridLayout_2 = QGridLayout(self.ax3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.dashboard_plot.addTab(self.ax3, "")
        self.ax4 = QWidget()
        self.ax4.setObjectName(u"ax4")
        self.gridLayout = QGridLayout(self.ax4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.dashboard_plot.addTab(self.ax4, "")

        self.verticalLayout.addWidget(self.dashboard_plot)

        self.result_table = QTableWidget(self.widget)
        if (self.result_table.columnCount() < 2):
            self.result_table.setColumnCount(2)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(0, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(1, __qtablewidgetitem2)
        self.result_table.setObjectName(u"result_table")
        self.result_table.setMouseTracking(True)
        self.result_table.setAutoFillBackground(True)
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.setTabKeyNavigation(True)
        self.result_table.setProperty(u"showDropIndicator", False)
        self.result_table.setDragDropOverwriteMode(False)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.result_table.setGridStyle(Qt.PenStyle.DashLine)
        self.result_table.setSortingEnabled(True)
        self.result_table.horizontalHeader().setProperty(u"showSortIndicator", False)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.verticalHeader().setProperty(u"showSortIndicator", False)

        self.verticalLayout.addWidget(self.result_table)

        self.hardening_table = QTableWidget(self.widget)
        if (self.hardening_table.columnCount() < 2):
            self.hardening_table.setColumnCount(2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.hardening_table.setHorizontalHeaderItem(0, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.hardening_table.setHorizontalHeaderItem(1, __qtablewidgetitem4)
        self.hardening_table.setObjectName(u"hardening_table")
        self.hardening_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.hardening_table.setTabKeyNavigation(True)
        self.hardening_table.setProperty(u"showDropIndicator", False)
        self.hardening_table.setDragDropOverwriteMode(False)
        self.hardening_table.setAlternatingRowColors(True)
        self.hardening_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.hardening_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.hardening_table.setGridStyle(Qt.PenStyle.DashLine)
        self.hardening_table.setSortingEnabled(True)
        self.hardening_table.horizontalHeader().setProperty(u"showSortIndicator", False)
        self.hardening_table.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.hardening_table)

        self.splitter.addWidget(self.widget)
        self.system_info = QTableWidget(self.splitter)
        if (self.system_info.columnCount() < 2):
            self.system_info.setColumnCount(2)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.system_info.setHorizontalHeaderItem(0, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.system_info.setHorizontalHeaderItem(1, __qtablewidgetitem6)
        self.system_info.setObjectName(u"system_info")
        self.system_info.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.system_info.setProperty(u"showDropIndicator", False)
        self.system_info.setDragDropOverwriteMode(False)
        self.system_info.setAlternatingRowColors(True)
        self.system_info.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.system_info.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.splitter.addWidget(self.system_info)
        self.system_info.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.splitter)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.submit_hardening = QPushButton(Zero_Security)
        self.submit_hardening.setObjectName(u"submit_hardening")

        self.horizontalLayout_4.addWidget(self.submit_hardening)

        self.hardening = QPushButton(Zero_Security)
        self.hardening.setObjectName(u"hardening")

        self.horizontalLayout_4.addWidget(self.hardening)

        self.check_security = QPushButton(Zero_Security)
        self.check_security.setObjectName(u"check_security")

        self.horizontalLayout_4.addWidget(self.check_security)

        self.check_security_result = QPushButton(Zero_Security)
        self.check_security_result.setObjectName(u"check_security_result")
        self.check_security_result.setAutoFillBackground(False)

        self.horizontalLayout_4.addWidget(self.check_security_result)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)


        self.gridLayout_4.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        QWidget.setTabOrder(self.path, self.browse)
        QWidget.setTabOrder(self.browse, self.dropbox)
        QWidget.setTabOrder(self.dropbox, self.submit)
        QWidget.setTabOrder(self.submit, self.path_table)
        QWidget.setTabOrder(self.path_table, self.check_security)
        QWidget.setTabOrder(self.check_security, self.result_table)
        QWidget.setTabOrder(self.result_table, self.cancel)
        QWidget.setTabOrder(self.cancel, self.check_security_result)

        self.retranslateUi(Zero_Security)
        self.cancel.clicked.connect(self.path.clear)
        self.cancel.clicked.connect(self.path_table.clearContents)
        self.cancel.clicked.connect(self.result_table.clearContents)

        self.dashboard_plot.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Zero_Security)
    # setupUi

    def retranslateUi(self, Zero_Security):
        Zero_Security.setWindowTitle(QCoreApplication.translate("Zero_Security", u"Digi Samurai", None))
        self.radio_local.setText(QCoreApplication.translate("Zero_Security", u"Use Local CIS PDF File", None))
        self.radio_online.setText(QCoreApplication.translate("Zero_Security", u"Download CIS PDF Online", None))
        self.browse.setText(QCoreApplication.translate("Zero_Security", u"Browse", None))
        self.dropbox.setItemText(0, QCoreApplication.translate("Zero_Security", u"Select", None))
        self.dropbox.setItemText(1, QCoreApplication.translate("Zero_Security", u"HKEY_CLASSES_ROOT", None))
        self.dropbox.setItemText(2, QCoreApplication.translate("Zero_Security", u"HKEY_CURRENT_USER", None))
        self.dropbox.setItemText(3, QCoreApplication.translate("Zero_Security", u"HKEY_LOCAL_MACHINE", None))
        self.dropbox.setItemText(4, QCoreApplication.translate("Zero_Security", u"HKEY_USERS", None))
        self.dropbox.setItemText(5, QCoreApplication.translate("Zero_Security", u"HKEY_CURRENT_CONFIG", None))

        self.cancel.setText(QCoreApplication.translate("Zero_Security", u"Cancel", None))
        self.submit.setText(QCoreApplication.translate("Zero_Security", u"Submit", None))
        self.backup_btn.setText(QCoreApplication.translate("Zero_Security", u"Backup Registry", None))
        ___qtablewidgetitem = self.path_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Zero_Security", u"Path", None))
        self.dashboard_plot.setTabText(self.dashboard_plot.indexOf(self.ax1), QCoreApplication.translate("Zero_Security", u"Detection Rate", None))
        self.dashboard_plot.setTabText(self.dashboard_plot.indexOf(self.ax2), QCoreApplication.translate("Zero_Security", u"Types of paths", None))
        self.dashboard_plot.setTabText(self.dashboard_plot.indexOf(self.ax3), QCoreApplication.translate("Zero_Security", u"System Categories", None))
        self.dashboard_plot.setTabText(self.dashboard_plot.indexOf(self.ax4), QCoreApplication.translate("Zero_Security", u"Software Categories", None))
        ___qtablewidgetitem1 = self.result_table.horizontalHeaderItem(0)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Zero_Security", u"Found", None))
        ___qtablewidgetitem2 = self.result_table.horizontalHeaderItem(1)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Zero_Security", u"Path", None))
        ___qtablewidgetitem3 = self.hardening_table.horizontalHeaderItem(0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Zero_Security", u"Hardening", None))
        ___qtablewidgetitem4 = self.hardening_table.horizontalHeaderItem(1)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Zero_Security", u"Path", None))
        ___qtablewidgetitem5 = self.system_info.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Zero_Security", u"Item", None))
        ___qtablewidgetitem6 = self.system_info.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Zero_Security", u"Values", None))
        self.submit_hardening.setText(QCoreApplication.translate("Zero_Security", u"Hardening", None))
        self.hardening.setText(QCoreApplication.translate("Zero_Security", u"Hardening", None))
        self.check_security.setText(QCoreApplication.translate("Zero_Security", u"Submit", None))
        self.check_security_result.setText(QCoreApplication.translate("Zero_Security", u"Dashboard", None))
    # retranslateUi

