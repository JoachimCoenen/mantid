#pylint: disable=invalid-name
"""
    Main window for reduction UIs
"""
from __future__ import (absolute_import, division, print_function)
import six
import sys
import os
import traceback

# Check whether Mantid is available
IS_IN_MANTIDPLOT = False
try:
    import mantidplot # noqa
    IS_IN_MANTIDPLOT = True
    from mantid.kernel import ConfigService
    from mantid.api import AlgorithmFactory
    CLUSTER_ENABLED = "SubmitRemoteJob" in AlgorithmFactory.getRegisteredAlgorithms(True)
except:
    import sip
    sip.setapi('QString',2)
    sip.setapi('QVariant',2)

from PyQt5 import QtGui, QtCore, QtWidgets # noqa
from PyQt5.QtCore import QObject

if six.PY3:
    unicode = str

REDUCTION_WARNING = False
WARNING_MESSAGE = ""

if IS_IN_MANTIDPLOT:
    try:
        import reduction
        if os.path.splitext(os.path.basename(reduction.__file__))[0] == "reduction":
            REDUCTION_WARNING = True
            home_dir = os.path.expanduser('~')
            if os.path.abspath(reduction.__file__).startswith(home_dir):
                WARNING_MESSAGE = "The following file is in your home area, please delete it and restart Mantid:\n\n"
            else:
                WARNING_MESSAGE = "If the following file is in your home area, please delete it and restart Mantid:\n\n"
            WARNING_MESSAGE += os.path.abspath(reduction.__file__)
    except:
        REDUCTION_WARNING = True
        WARNING_MESSAGE = "Please contact the Mantid team with the following message:\n\n\n"
        WARNING_MESSAGE += unicode(traceback.format_exc())

from reduction_gui.instruments.instrument_factory import instrument_factory, INSTRUMENT_DICT # noqa
from reduction_gui.settings.application_settings import GeneralSettings # noqa
import ui.ui_reduction_main # noqa
import ui.ui_instrument_dialog # noqa
import ui.ui_cluster_details_dialog # noqa

from functionalStyleGUI import FunctionalStyleGUI

class ReductionGUI(QtWidgets.QMainWindow):
    def __init__(self, instrument = None, facility = None, instrument_list=None):
        QtWidgets.QMainWindow.__init__(self)

        if REDUCTION_WARNING:
            message = "The reduction application has problems starting:\n\n"
            message += WARNING_MESSAGE
            QtWidgets.QMessageBox.warning(self, "WARNING", message)

        # Application settings
        settings = QtCore.QSettings()

        if instrument_list is not None and instrument not in instrument_list:
            instrument = None

        self._instrument = instrument
        self._facility = facility

        # List of allowed instrument
        self._instrument_list = instrument_list

        # Reduction interface
        self._interface = None

        # Recent files
        self._recent_files = settings.value("recent_files", [])
        if self._recent_files is None:  # An empty list saved to QSettings comes back as 'None'
            self._recent_files = []

        # Folder to open files in
        self._last_directory = unicode(settings.value("last_directory", '.'))
        self._last_export_directory = unicode(settings.value("last_export_directory", '.'))

        # Current file name
        self._filename = None

        # Cluster credentials and options
        self._cluster_details_set = False
        self._number_of_nodes = 1
        self._cores_per_node = 16
        self._compute_resources = ['Fermi']
        if IS_IN_MANTIDPLOT \
                and hasattr(ConfigService.Instance().getFacility(), "computeResources"):
                self._compute_resources = ConfigService.Instance().getFacility().computeResources()

        # Internal flag for clearing all settings and restarting the application
        self._clear_and_restart = False

        # General settings shared by all widgets
        self.general_settings = GeneralSettings(settings)

        #self.setupUi(self)
        
        # Event connections
        #if not IS_IN_MANTIDPLOT:
        #    self.reduce_button.hide()
        #self.cluster_button.hide()
        #self.export_button.clicked.connect(self._export)
        #self.reduce_button.clicked.connect(self.reduce_clicked)
        #self.save_button.clicked.connect(self._save)
        #self.interface_chk.clicked.connect(self._interface_choice)

        #self.interface_chk.setChecked(self.general_settings.advanced)

        # Of the widgets that are part of the application, one is the ApplicationWindow.
        # The ApplicationWindow will send a shutting_down() signal when quitting,
        # after which we should close this window.
        # Note: there is no way to identify which Widget is the ApplicationWindow.
        for w in QtCore.QCoreApplication.instance().topLevelWidgets():
            if hasattr(w, "shutting_down"):
                w.shutting_down.connect(self.close)

        #self.general_settings.progress.connect(self._progress_updated)

        #Main Menu:
        self._fileMenu = self.menuBar().addMenu('File')
        self._toolsMenu = self.menuBar().addMenu('Tools')

        #GUI
        self._isClusterButtonVisible = False
        self._isProgressBarVisible = False
        self.setCentralWidget(QtWidgets.QWidget(self))
        self._gui = FunctionalStyleGUI(self.centralWidget(), self.OnGUI)
        self._gui.redrawGUI()

    def OnGUI(self):
        gui = self._gui

        with gui.vLayout():
            tabs = []
            if self._interface != None:
                tabs = self._interface.get_tabs()

                if len(tabs) == 1:
                    gui.customWidget(tabs[0][1], fullSize=True)
                else:
                    with gui.tabWidget(fullSize=True) as tabWidget:
                        for tab in tabs:
                            with tabWidget.addTab(tab[0]):
                                gui.customWidget(tab[1])
            
            # footer:
            with gui.hLayout():
                if self._interface == None or self._interface.has_advanced_version():
                    newInterfaceChoice = gui.checkBox(self.general_settings.advanced, label='Advanced Interface')
                    if newInterfaceChoice != self.general_settings.advanced:
                        self.general_settings.advanced = newInterfaceChoice
                        self._interface_choiceChanged()
                #    
                gui.addSpacer(40, QtWidgets.QSizePolicy.Expanding)
                if self._isProgressBarVisible:
                    gui.progressBar(self.general_settings.progress)
                gui.addSpacer(40, QtWidgets.QSizePolicy.Fixed)
                #
                if gui.button('Reduce'):
                    self.reduce_clicked()
                if self._isClusterButtonVisible:
                    if gui.button('Send Cluster'):
                        self.cluster_clicked()
                if gui.button('Save'):
                    self._save()
                if gui.button('Export'):
                    self._export()

    def _set_window_title(self):
        """
            Sets the window title using the instrument name and the
            current settings file
        """
        title = "%s Reduction" % self._instrument
        if self._filename is not None:
            title += ": %s" % self._filename
        self.setWindowTitle(title)

    def _progress_updated(self, value):
        self.progress_bar.setValue(value)
        #done

    def setup_layout(self, load_last=False):
        """
            Sets up the instrument-specific part of the UI layout
        """
        # Clean up the widgets that have already been created
        #self.tabWidget.clear()
        self._isProgressBarVisible = False

        if self._instrument == '' or self._instrument is None:
            return self._change_instrument()

        self._update_file_menu()

        if self._interface is not None:
            self._interface.destroy()

        self.general_settings.instrument_name = self._instrument
        # Find corresponding facility
        if self._facility is None:
            for facility in INSTRUMENT_DICT.keys():
                if self._instrument in INSTRUMENT_DICT[facility].keys():
                    self._facility = facility
                    break
        if self._facility is None:
            self._facility = ConfigService.Instance().getFacility().name()

        self.general_settings.facility_name = self._facility
        self._interface = instrument_factory(self._instrument, settings=self.general_settings)

        if self._interface is not None:
            #tab_list = self._interface.get_tabs()
            #for tab in tab_list:
            #    self.tabWidget.addTab(tab[1], tab[0])
            self._set_window_title()

            # Show the "advanced interface" check box if needed
            #if self._interface.has_advanced_version():
            #    self.interface_chk.show()
            #else:
            #    self.interface_chk.hide()

            # Show the parallel reduction button if enabled
            if self._interface.is_cluster_enabled() and IS_IN_MANTIDPLOT \
                    and CLUSTER_ENABLED:
                config = ConfigService.Instance()
                self._isClusterButtonVisible = \
                config.hasProperty("cluster.submission") and config.getString("cluster.submission").lower()=='on'
                #self.cluster_button.show()
                #self.cluster_button.clicked.connect(self.cluster_clicked)
            else:
                self._isClusterButtonVisible = False
                #self.cluster_button.hide()

            if load_last:
                self._interface.load_last_reduction()
        else:
            print("Could not generate an interface for instrument %s" % self._instrument)
            self.close()

        self._gui.redrawGUI()
        return True

    def _update_file_menu(self):
        """
            Set up the File menu and update the menu with recent files
        """
        self._fileMenu.clear()

        newAction = QtWidgets.QAction("&New Reduction...", self)
        newAction.setShortcut("Ctrl+N")
        newAction.setStatusTip("Start a new reduction")
        newAction.triggered.connect(self._new)

        openAction = QtWidgets.QAction("&Open...", self)
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip("Open an XML file containing reduction parameters")
        openAction.triggered.connect(self._file_open)

        saveAsAction = QtWidgets.QAction("Save as...", self)
        saveAsAction.setStatusTip("Save the reduction parameters to XML")
        saveAsAction.triggered.connect(self._save_as)

        saveAction = QtWidgets.QAction("&Save...", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip("Save the reduction parameters to XML")
        saveAction.triggered.connect(self._save)

        exportAction = QtWidgets.QAction("&Export...", self)
        exportAction.setShortcut("Ctrl+E")
        exportAction.setStatusTip("Export to python script for Mantid")
        exportAction.triggered.connect(self._export)

        quitAction = QtWidgets.QAction("&Quit", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.close)

        self._fileMenu.addAction(newAction)
        self._fileMenu.addAction(openAction)
        self._fileMenu.addAction(saveAction)
        self._fileMenu.addAction(saveAsAction)
        self._fileMenu.addAction(exportAction)
        self._fileMenu.addSeparator()

        if self.general_settings.debug:
            clearAction = QtWidgets.QAction("&Clear settings and quit", self)
            clearAction.setStatusTip("Restore initial application settings and close the application")
            clearAction.triggered.connect(self._clear_and_close)
            self._fileMenu.addAction(clearAction)

        self._fileMenu.addAction(quitAction)

        # TOOLS menu
        instrAction = QtWidgets.QAction("Change &instrument...", self)
        instrAction.setShortcut("Ctrl+I")
        instrAction.setStatusTip("Select a new instrument")
        instrAction.triggered.connect(self._change_instrument)

        debug_menu_item_str = "Turn debug mode ON"
        if self.general_settings.debug:
            debug_menu_item_str = "Turn debug mode OFF"
        debugAction = QtWidgets.QAction(debug_menu_item_str, self)
        debugAction.setStatusTip(debug_menu_item_str)
        debugAction.triggered.connect(self._debug_mode)

        self._toolsMenu.clear()
        self._toolsMenu.addAction(instrAction)
        self._toolsMenu.addAction(debugAction)

        # Cluster submission details
        if IS_IN_MANTIDPLOT and CLUSTER_ENABLED:
            jobAction = QtWidgets.QAction("Remote submission details", self)
            jobAction.setShortcut("Ctrl+R")
            jobAction.setStatusTip("Set the cluster information for remote job submission")
            jobAction.triggered.connect(self._cluster_details_dialog)
            self._toolsMenu.addAction(jobAction)

        recent_files = []
        for fname in self._recent_files:
            if fname != self._filename and QtCore.QFile.exists(fname) and fname not in recent_files:
                recent_files.append(fname)

        if len(recent_files)>0:
            self._fileMenu.addSeparator()
            for i, fname in enumerate(recent_files):
                action = QtWidgets.QAction("&%d %s" % (i+1, QtCore.QFileInfo(fname).fileName()), self)
                action.setData(fname)
                action.triggered.connect(self.open_file)
                self._fileMenu.addAction(action)

    def _debug_mode(self, mode=None):
        """
            Set debug mode
            @param mode: debug mode (True or False). If None, the debug mode will simply be flipped
        """
        if mode is None:
            mode = not self.general_settings.debug
        self.general_settings.debug = mode
        self._new()
        self.setup_layout()

    def _interface_choiceChanged(self):
        self._new()
        self.setup_layout()

    def _change_instrument(self):
        """
            Invoke an instrument selection dialog
        """
        class InstrDialog(QtWidgets.QDialog):
            def __init__(self, instrument_list=None):
                QtWidgets.QDialog.__init__(self)
                self.instrument_list = instrument_list
                print("@@@@@@", (InstrDialog), "@@@@@@")
                #values:
                self.facilities = sorted(INSTRUMENT_DICT.keys())
                self.facilities.reverse()
                self.facility = ''
                self.instrument = ''
                #GUI:
                self._gui = FunctionalStyleGUI(self, self.OnGUI)
                self._gui.redrawGUI()
                self.resize(318, 137)

            def OnGUI(self):
                gui = self._gui
                print( self.facilities)
                self.facility = gui.comboBox(self.facility, self.facilities, label='Facility')

                instruments = filter(lambda item:  self.instrument_list is None or item in self.instrument_list, sorted(INSTRUMENT_DICT[unicode(self.facility)].keys()))
                self.instrument = gui.comboBox(self.instrument, instruments, label='Instrument')

                with gui.hLayout():
                    if gui.button('OK'):
                        self.accept()
                    if gui.button('Cancel'):
                        self.reject()
                

        if self.general_settings.debug:
            dialog = InstrDialog()
        else:
            dialog = InstrDialog(self._instrument_list)
        dialog.exec_()
        if dialog.result()==1:
            #self._instrument = dialog.instr_combo.currentText()
            #self._facility = dialog.facility_combo.currentText()
            self._instrument = dialog.instrument
            self._facility = dialog.facility
            self.setup_layout()
            self._new()
            return True
        else:
            self.close()
            return False

    def _cluster_details_dialog(self):
        """
            Show dialog to get cluster submission details
        """
        class ClusterDialog(QtWidgets.QDialog, ui.ui_cluster_details_dialog.Ui_Dialog):
            def __init__(self, compute_resources=None):
                QtWidgets.QDialog.__init__(self)
                self.setupUi(self)
                self.resource_combo.clear()
                for res in compute_resources:
                    self.resource_combo.addItem(QtWidgets.QApplication.translate("Dialog", res, None))

        # Fill out the defaults
        dialog = ClusterDialog(self._compute_resources)
        if self.general_settings.cluster_user is not None:
            dialog.username_edit.setText(str(self.general_settings.cluster_user))
            dialog.pass_edit.setText(str(self.general_settings.cluster_pass))

        dialog.nodes_box.setValue(int(self._number_of_nodes))
        dialog.cores_box.setValue(int(self._cores_per_node))
        for i in range(dialog.resource_combo.count()):
            if dialog.resource_combo.itemText(i)==self.general_settings.compute_resource:
                dialog.resource_combo.setCurrentIndex(i)
                break

        dialog.exec_()
        if dialog.result()==1:
            self.general_settings.cluster_user = str(dialog.username_edit.text())
            self.general_settings.cluster_pass = str(dialog.pass_edit.text())
            self._cluster_details_set = True
            self._number_of_nodes = int(dialog.nodes_box.value())
            self._cores_per_node = int(dialog.cores_box.value())
            self.general_settings.compute_resource = dialog.resource_combo.currentText()

    def _clear_and_close(self):
        """
            Clear all QSettings parameters
        """
        self._clear_and_restart = True
        self.close()
        # If we make it here, the user canceled the close, which
        # means that we need to reset the clear&close flag so
        # that the state is properly saved on the next close.
        self._clear_and_restart = False

    def closeEvent(self, event):
        """
            Executed when the application closes
        """
        if False:
            reply = QtWidgets.QMessageBox.question(self, 'Message',
                                               "Are you sure you want to quit this application?",
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

        # Save application settings
        if self._clear_and_restart:
            self._clear_and_restart = False
            QtCore.QSettings().clear()
        else:
            settings = QtCore.QSettings()

            settings.setValue("instrument_name", self._instrument)
            settings.setValue("last_file", self._filename)
            settings.setValue("recent_files", self._recent_files)
            settings.setValue("last_directory", str(self._last_directory))
            settings.setValue("last_export_directory", str(self._last_export_directory))

    def reduce_clicked(self):
        """
            Create an object capable of using the information in the
            interface and turn it into a reduction process.
        """
        #self.reduce_button.setEnabled(False)
        #self.export_button.setEnabled(False)
        #self.save_button.setEnabled(False)
        #self.interface_chk.setEnabled(False)
        self._fileMenu.setEnabled(False)
        self._toolsMenu.setEnabled(False)

        if self._interface is not None:
            self._interface.reduce()

        #self.reduce_button.setEnabled(True)
        #self.export_button.setEnabled(True)
        #self.save_button.setEnabled(True)
        #self.interface_chk.setEnabled(True)
        self._fileMenu.setEnabled(True)
        self._toolsMenu.setEnabled(True)

    def cluster_clicked(self):
        """
            Submit for parallel reduction
        """
        if not self._cluster_details_set:
            self._cluster_details_dialog()

        if self._interface is not None \
                and self.general_settings.cluster_user is not None \
                and self.general_settings.cluster_pass is not None:
            # Chose a name for the job
            if self._filename is not None:
                job_name = os.path.basename(self._filename).strip()
                toks = os.path.splitext(job_name)
                job_name = toks[0]
            else:
                job_name = ''
            self._interface.cluster_submit(self.general_settings.cluster_user,
                                           self.general_settings.cluster_pass,
                                           resource=self.general_settings.compute_resource,
                                           nodes=self._number_of_nodes,
                                           cores_per_node=self._cores_per_node,
                                           job_name=job_name)

    def open_file(self, file_path=None):
        """
            Open an XML file and populate the UI
            @param file_path: path to the file to be loaded
        """
        if file_path is None:
            action = self.sender()
            if isinstance(action, QtWidgets.QAction):
                file_path = unicode(action.data())

        # don't try to load if the file doesn't exist
        if not os.path.exists(file_path):
            return

        # Check whether the file describes the current instrument
        try:
            found_instrument = self._interface.scripter.verify_instrument(file_path)
        except:
            msg = "The file you attempted to load doesn't have a recognized format:\n" \
                  + file_path+"\n\n" \
                  + "Please make sure it has been produced by this application."
            QtWidgets.QMessageBox.warning(self, "Error loading reduction parameter file", msg)
            print(sys.exc_info()[1])
            return

        if not found_instrument == self._instrument:
            self._instrument = found_instrument
            self.setup_layout()

        self.reduce_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.interface_chk.setEnabled(False)
        self._interface.load_file(file_path)
        self.reduce_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.interface_chk.setEnabled(True)

        self._filename = file_path
        self._update_file_menu()
        self._set_window_title()

        if file_path in self._recent_files:
            self._recent_files.remove(file_path)
        self._recent_files.insert(0,file_path)
        while len(self._recent_files) > 10:
            self._recent_files.pop()

    def _new(self, *argv):
        """
            Start new reduction
        """
        self._interface.reset()
        self._filename = None
        self._update_file_menu()
        self._set_window_title()

    def _file_open(self, *argv):
        """
            File chooser for loading UI parameters
        """
        fname_qstr = QtWidgets.QFileDialog.getOpenFileName(self, "Reduction settings - Choose a settings file",
                                                       self._last_directory,
                                                       "Settings files (*.xml)")[0]
        fname = str(QtCore.QFileInfo(fname_qstr).filePath())
        if fname:
            # Store the location of the loaded file
            self._last_directory = str(QtCore.QFileInfo(fname_qstr).path())
            self.open_file(fname)

    def _save(self):
        """
            Present a file dialog to the user and saves the content of the
            UI in XML format
        """
        if self._filename is None:
            self._save_as()
        else:
            try:
                self._interface.save_file(self._filename)
                self._update_file_menu()
                self.statusBar().showMessage("Saved as %s" % self._filename)
                self._set_window_title()
            except:
                #TODO: put this in a log window, and in a file
                print(sys.exc_info()[1])
                self.statusBar().showMessage("Failed to save %s" % self._filename)

    def _save_as(self):
        """
            Present a file dialog to the user and saves the content of
            the UI in XML format.
        """
        if self._filename is not None:
            fname = self._filename
        else:
            fname = self._instrument + '_'

        fname_qstr = QtWidgets.QFileDialog.getSaveFileName(self, "Reduction settings - Save settings",
                                                       self._last_directory + '/' + fname,
                                                       "Settings files (*.xml)")[0]
        fname = str(QtCore.QFileInfo(fname_qstr).filePath())
        if len(fname)>0:
            if not fname.endswith('.xml'):
                fname += ".xml"
            if fname in self._recent_files:
                self._recent_files.remove(fname)
            self._recent_files.insert(0,fname)
            while len(self._recent_files) > 10:
                self._recent_files.pop()
            self._last_directory = str(QtCore.QFileInfo(fname_qstr).path())
            self._filename = fname
            self._save()

    def _export(self):
        """
            Exports the current content of the UI to a python script that can
            be run within MantidPlot
        """
        if self._interface is None:
            return

        fname = '.'
        if self._filename is not None:
            (root, ext) = os.path.splitext(self._filename)
            fname = root

        fname = unicode(QtWidgets.QFileDialog.getSaveFileName(self, "Mantid Python script - Save script",
                                                          self._last_export_directory,
                                                          "Python script (*.py)")[0])

        if len(fname)>0:
            if not fname.endswith('.py'):
                fname += ".py"
            (folder, file_name) = os.path.split(fname)
            self._last_export_directory = folder
            script = self._interface.export(fname)
            if script is not None:
                self.statusBar().showMessage("Saved as %s" % fname)
            else:
                self.statusBar().showMessage("Could not save file")

#--------------------------------------------------------------------------------------------------------


def start(argv):
    app = QtWidgets.QApplication(argv)
    app.setOrganizationName("Mantid")
    app.setOrganizationDomain("mantidproject.org")
    app.setApplicationName("Mantid Reduction")

    # Application settings
    settings = QtCore.QSettings()

    # Name handle for the instrument
    instrument = unicode(settings.value("instrument_name", ''))

    reducer = ReductionGUI(instrument=instrument)
    reducer.setup_layout(load_last=True)
    reducer.show()
    app.exec_()


if __name__ == '__main__':
    start(argv=sys.argv)
