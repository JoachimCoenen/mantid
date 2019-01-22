from __future__ import (absolute_import, division, print_function)

from qtpy import QtWidgets, QtCore

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from MultiPlotting.navigation_toolbar import myToolbar

# use this to manage lines and workspaces directly

# visualises multiple plots


class subPlot(QtWidgets.QWidget):
    quickEditSignal = QtCore.Signal(object)

    def __init__(self, context):
        super(subPlot, self).__init__()
        self._context = context
        self.figure = Figure()
        self.figure.set_facecolor("none")
        self.canvas = FigureCanvas(self.figure)
        # update quick edit from tool bar
        self.canvas.mpl_connect("draw_event", self.draw_event_callback)

        grid = QtWidgets.QGridLayout()
        # add toolbar
        self.toolbar = myToolbar(self.canvas, self)
        self.toolbar.update()
        grid.addWidget(self.toolbar, 0, 0)
        # add plot
        self.plotObjects = {}
        grid.addWidget(self.canvas, 1, 0)
        self.setLayout(grid)

    """ this is called when the zoom
    or pan are used. We want to send a
    signal to update the axis ranges """

    def draw_event_callback(self, event):
        self.figure.tight_layout()
        for subplot in self.plotObjects.keys():
            self.emit_subplot_range(subplot)

    # plot a workspace, if a new subplot create it.
    def plot(self, subplotName, workspace, specNum=1):
        new = False
        if subplotName not in self._context.subplots.keys():
            self.add_subplot(subplotName)
            new = True
        self._add_plotted_line(subplotName, workspace, specNum=specNum)
        if new:
            self.emit_subplot_range(subplotName)

    def change_errors(self, state, subplotNames):
        for subplotName in subplotNames:
            self._context.subplots[subplotName].change_errors(state)
            self.canvas.draw()

    # adds plotted line to context and updates GUI
    def _add_plotted_line(self, subplotName, workspace, specNum):
        """ Appends plotted lines to the related subplot list. """
        self._context.addLine(subplotName, workspace, specNum)
        self.canvas.draw()

    def add_subplot(self, subplotName, code=111):
        self.plotObjects[subplotName] = self.figure.add_subplot(code)
        self.plotObjects[subplotName].set_title(subplotName)
        self._context.addSubplot(subplotName, self.plotObjects[subplotName])
        self.figure.tight_layout()

    def emit_subplot_range(self, subplotName):
        self.quickEditSignal.emit(subplotName)

    def set_plot_x_range(self, subplotNames, range):
        for subplotName in subplotNames:
            # make a set method in context and set it there
            self.plotObjects[subplotName].set_xlim(range)
            self.canvas.draw()

    def set_plot_y_range(self, subplotNames, range):
        for subplotName in subplotNames:
            self.plotObjects[subplotName].set_ylim(range)
            self.canvas.draw()

    def connect_quick_edit_signal(self, slot):
        self.quickEditSignal.connect(slot)

    def disconnect_quick_edit_signal(self, slot):
        self.quickEditSignal.disconnect(slot)

    def set_y_autoscale(self, subplotNames, state):
        for subplotName in subplotNames:
            self._context.subplots[subplotName].change_auto(state)
            self.canvas.draw()
