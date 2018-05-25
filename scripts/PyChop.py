# pylint: disable=line-too-long, invalid-name, unused-import

"""
Module to import and run the PyChop GUI for use either on the commandline or as a MantidPlot interface
"""

import sys
from PyQt5 import QtGui
from PyChop import PyChopGui

if __name__ == '__main__':
    if QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication.instance()
    else:
        app = QtWidgets.QApplication(sys.argv)
    window = PyChopGui.PyChopGui()
    window.show()
    try: # check if started from within mantidplot
        import mantidplot # noqa
    except ImportError:
        sys.exit(app.exec_())
