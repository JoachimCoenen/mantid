from __future__ import (absolute_import, division, print_function)

from PyQt5 import QtCore, QtGui, QtWidgets


class TransformSelectionView(QtWidgets.QWidget):
    """
    Create the transformation selection widget's appearance
    """
    # signals
    changeMethodSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(TransformSelectionView, self).__init__(parent)
        self.grid = QtWidgets.QGridLayout(self)
        self.methods = QtWidgets.QComboBox()
        # default to FFT
        options=["FFT"]
        self.methods.addItems(options)
        self.grid.addWidget(self.methods)
        self.methods.currentIndexChanged.connect(self.sendSignal)

    # sets the methods in the selection widget
    def setMethodsCombo(self,options):
        self.methods.clear()
        self.methods.addItems(options)

    def sendSignal(self,index):
        self.changeMethodSignal.emit(index)
