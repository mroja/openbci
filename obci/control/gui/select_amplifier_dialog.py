# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'select_amplifier_dialog.ui'
#
# Created: Sun Aug 10 14:56:36 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_SelectAmplifier(object):

    def setupUi(self, SelectAmplifier):
        SelectAmplifier.setObjectName("SelectAmplifier")
        SelectAmplifier.resize(400, 300)
        self.verticalLayout_2 = QtGui.QVBoxLayout(SelectAmplifier)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtGui.QGroupBox(SelectAmplifier)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.refreshButton = QtGui.QPushButton(self.groupBox)
        self.refreshButton.setObjectName("refreshButton")
        self.verticalLayout.addWidget(self.refreshButton)
        self.amplifiers = QtGui.QTableWidget(self.groupBox)
        self.amplifiers.setObjectName("amplifiers")
        self.amplifiers.setColumnCount(0)
        self.amplifiers.setRowCount(0)
        self.verticalLayout.addWidget(self.amplifiers)
        self.buttonBox = QtGui.QDialogButtonBox(self.groupBox)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(SelectAmplifier)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), SelectAmplifier.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), SelectAmplifier.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectAmplifier)

    def retranslateUi(self, SelectAmplifier):
        SelectAmplifier.setWindowTitle(_translate("SelectAmplifier", "Select Amplifier", None))
        self.groupBox.setTitle(_translate("SelectAmplifier", "Amplifiers", None))
        self.refreshButton.setText(_translate("SelectAmplifier", "Refresh", None))
