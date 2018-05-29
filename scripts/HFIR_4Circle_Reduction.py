#pylint: disable=invalid-name
from __future__ import (absolute_import, division, print_function)
from HFIR_4Circle_Reduction import reduce4circleGUI
from PyQt5 import QtWidgets, QtCore, QtGui
import sys


def qapp():
    if QtWidgets.QApplication.instance():
        _app = QtWidgets.QApplication.instance()
    else:
        _app = QtWidgets.QApplication(sys.argv)
    return _app


# try to defeat X11 unsafe thread
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
app = qapp()

reducer = reduce4circleGUI.MainWindow() #the main ui class in this file is called MainWindow
reducer.show()
app.exec_()
