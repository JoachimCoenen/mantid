#pylint: disable=invalid-name,unused-import
from __future__ import (absolute_import, division, print_function)
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from DGSPlanner import DGSPlannerGUI


def qapp():
    if QtWidgets.QApplication.instance():
        _app = QtWidgets.QApplication.instance()
    else:
        _app = QtWidgets.QApplication(sys.argv)
    return _app


if __name__ == '__main__':
    app = qapp()
    planner = DGSPlannerGUI.DGSPlannerGUI()
    planner.show()
    try: #check if started from within mantidplot
        import mantidplot # noqa
    except ImportError:
        sys.exit(app.exec_())
