#pylint: disable=invalid-name
from __future__ import (absolute_import, division, print_function)

import sys

import PyQt5.QtGui as QtGui

from Muon import model_constructor
from Muon import transform_presenter
from Muon import transform_view
from Muon import view_constructor


class FrequencyDomainAnalysisGui(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(FrequencyDomainAnalysisGui,self).__init__(parent)

        groupedViews = view_constructor.ViewConstructor(True,self)
        groupedModels = model_constructor.ModelConstructor(True)
        view =transform_view.TransformView(groupedViews,self)
        self.presenter =transform_presenter.TransformPresenter(view,groupedModels)

        self.setCentralWidget(view)
        self.setWindowTitle("Frequency Domain Analysis")

    # cancel algs if window is closed
    def closeEvent(self,event):
        self.presenter.close()


def qapp():
    if QtWidgets.QApplication.instance():
        _app = QtWidgets.QApplication.instance()
    else:
        _app = QtWidgets.QApplication(sys.argv)
    return _app


app = qapp()
try:
    ex= FrequencyDomainAnalysisGui()
    ex.resize(700,700)
    ex.show()
    app.exec_()
except RuntimeError as error:
    ex = QtWidgets.QWidget()
    QtWidgets.QMessageBox.warning(ex,"Frequency Domain Analysis",str(error))
