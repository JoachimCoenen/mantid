
from PyQt5 import QtWidgets, QtCore, QtGui


def warning(error):

    ex = QtWidgets.QWidget()
    QtWidgets.QMessageBox.warning(ex, "Frequency Domain Analysis", str(error))
