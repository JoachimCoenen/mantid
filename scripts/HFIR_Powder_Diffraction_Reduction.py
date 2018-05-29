#pylint: disable=invalid-name,no-name-in-module
"""
    Script used to start the DGS reduction GUI from MantidPlot
"""
from __future__ import (absolute_import, division, print_function)
import sys

from HFIRPowderReduction import HfirPDReductionGUI
from PyQt5 import QtWidgets, QtCore, QtGui


def qapp():
    if QtWidgets.QApplication.instance():
        _app = QtWidgets.QApplication.instance()
    else:
        _app = QtWidgets.QApplication(sys.argv)
    return _app


app = qapp()

reducer = HfirPDReductionGUI.MainWindow() #the main ui class in this file is called MainWindow
reducer.show()

app.exec_()
