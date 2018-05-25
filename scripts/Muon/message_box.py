import PyQt5.QtGui as QtGui


def warning(error):

    ex = QtWidgets.QWidget()
    QtWidgets.QMessageBox.warning(ex, "Frequency Domain Analysis", str(error))
