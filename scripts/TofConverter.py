#pylint: disable=invalid-name
from __future__ import (absolute_import, division, print_function)
from TofConverter import converterGUI
from PyQt5 import QtWidgets, QtCore, QtGui
import sys


def qapp():
    if QtWidgets.QApplication.instance():
        _app = QtWidgets.QApplication.instance()
    else:
        _app = QtWidgets.QApplication(sys.argv)
    return _app


app = qapp()
reducer = converterGUI.MainWindow()#the main ui class in this file is called MainWindow
reducer.show()
app.exec_()
