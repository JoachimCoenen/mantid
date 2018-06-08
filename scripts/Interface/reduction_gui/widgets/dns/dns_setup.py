from PyQt5.QtWidgets import QLineEdit, QPushButton, QTableView, QHeaderView, QCheckBox, QDoubleSpinBox, QRadioButton, \
    QLayout, QWidget, QSpacerItem, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QGroupBox, QGridLayout, QButtonGroup, \
    QSizePolicy, QMessageBox, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, QModelIndex, Qt
from PyQt5 import QtWidgets, QtCore, QtGui

from reduction_gui.widgets.base_widget import BaseWidget
from reduction_gui.reduction.dns.dns_reduction import DNSScriptElement

import os
import re

from functionalStyleGUI import FunctionalStyleGUI

class DNSSetupWidget(BaseWidget):
    """
    Widget that presents the options for DNS-Reduction
    """

    # Widget name
    name = "DNS Reduction"

    # Tips for the user how to fill in the data

    TIP_sampleDataPath    = ""
    TIP_btnSampleDataPath = ""
    TIP_sampleFilePre     = ""
    TIP_sampleFileSuff    = ""
    TIP_runsView          = ""

    TIP_maskAngle = ""

    TIP_chkSaveToFile = ""
    TIP_outDir        = ""
    TIP_btnOutDir     = ""
    TIP_outFile       = ""

    TIP_standardDataPath    = ""
    TIP_btnStandardDataPath = ""

    TIP_chkDetEffi     = ""
    TIP_chkSumVan      = ""
    TIP_chkSubInst     = ""
    TIP_subFac         = ""
    TIP_chkFlipRatio  = ""
    TIP_flipFac       = ""
    TIP_multiSF        = ""
    TIP_rbnNormTime    = ""
    TIP_rbnNormMonitor = ""
    TIP_neutronWaveLen = ""

    TIP_rbnPolyAmor = ""

    TIP_chkAxQ      = ""
    TIP_chkAxD      = ""
    TIP_chkAx2Theta = ""
    TIP_rbnXYZ      = ""
    TIP_rbnCoherent = ""
    TIP_rbnNo       = ""

    TIP_rbnSingleCryst = ""

    TIP_omegaOffset  = ""
    TIP_latticeA     = ""
    TIP_latticeB     = ""
    TIP_latticeC     = ""
    TIP_latticeAlpha = ""
    TIP_latticeBeta  = ""
    TIP_latticeGamma = ""
    TIP_scatterU1    = ""
    TIP_scatterU2    = ""
    TIP_scatterU3    = ""
    TIP_scatterV1    = ""
    TIP_scatterV2    = ""
    TIP_scatterV3    = ""

    def __init__(self, settings):
        BaseWidget.__init__(self, settings=settings)
        self.newDNSScriptElement()

        #GUI
        self._recDepth = 0
        self.gui = FunctionalStyleGUI(self, self.OnGUI)
        self.gui.redrawGUI()
        return

    def OnGUI(self):
        if self.elem == None:
            self.newDNSScriptElement()
        gui = self.gui
        elem = self.elem

        with gui.tabWidget() as tabWidget:
            with tabWidget.addTab('Data'):
                self._leftGUI()
            with tabWidget.addTab('Reduction Settings', preventVStretch = True):
                self._rightGUI()
        return

    def _leftGUI(self):
        elem = self.elem
        gui = self.gui

        with gui.groupBox('Sample data'):
            elem.sampleDataPath = gui.folderPathEdit(elem.sampleDataPath, label='Data Directory', tip=self.TIP_sampleDataPath)
            gui.helpBoxRight(self.check_sampleDataPath(elem), style='error')
            with gui.hLayoutLabeled(label='File Prefix', tip=self.TIP_sampleFilePre):
                elem.filePrefix = gui.lineEdit(elem.filePrefix, tip=self.TIP_sampleFilePre)
                elem.fileSuffix = gui.lineEdit(elem.fileSuffix, label='suffix', tip=self.TIP_sampleFileSuff)
            gui.helpBoxRight(self.check_filePrefixSuffix(elem), style='error')

            elem.dataRuns = gui.dataTable(elem.dataRuns, ("Run numbers", "Output Workspace", "Comment"), tip=self.TIP_runsView)
            gui.helpBox(self.check_dataRuns(elem), style='error')

        with gui.groupBox('Mask Detectors'):
            elem.maskAngles  = gui.dataTable(elem.maskAngles, (u"Min Angle[\305]", u"Max Angle[\305]"), tip=self.TIP_runsView)
            gui.helpBox(self.check_maskAngles(elem), style='error')

        with gui.groupBoxChecked(elem.saveToFile, title='Save to file') as elem.saveToFile:
            gui.helpBox(self.check_saveToFile(elem), style='error')
            elem.outDir = gui.folderPathEdit(elem.outDir, label='Output Directory', tip=self.TIP_outDir, enabled=elem.saveToFile)
            elem.outPrefix = gui.lineEdit(elem.outPrefix, label='Output File Prefix', tip=self.TIP_outFile, enabled=elem.saveToFile)

    def _rightGUI(self):
        elem = self.elem
        gui = self.gui
        
        with gui.groupBox('Standard Data'):
            elem.standardDataPath = gui.folderPathEdit(elem.standardDataPath, label='Path', tip=self.TIP_standardDataPath)
            gui.helpBoxRight(self.check_standardDataPath(elem), style='error')

        with gui.groupBox('Data Reduction Settings', preventHStretch=True):
            elem.detEffi    = gui.checkBox(elem.detEffi,   label='Detector efficiency correction', tip=self.TIP_chkDetEffi)
            with gui.indentation():
                elem.sumVan     = gui.checkBox(elem.sumVan,    label='Sum Vanadium over detector position (future)', tip=self.TIP_chkSumVan, enabled=False)
            elem.subInst    = gui.checkBox(elem.subInst,   label='Subtract instrument background for sample', tip=self.TIP_chkSubInst)
            with gui.indentation():
                elem.subFac     = gui.doubleSpinBox(elem.subFac, minVal=0, decimals= 2, label='Factor', tip=self.TIP_subFac, enabled= elem.subInst)
            elem.flipRatio  = gui.checkBox(elem.flipRatio, label='Flipping ratio correction',  tip=self.TIP_chkFlipRatio)
            with gui.indentation():
                elem.flipFac    = gui.doubleSpinBox(elem.flipFac, minVal=0, decimals= 2, label='Factor', tip=self.TIP_flipFac, enabled=elem.flipRatio)
            elem.multiSF    = gui.doubleSpinBox(elem.multiSF, minVal=0, maxVal=1, decimals= 2, label='Mult. SF scattering prob.', tip=self.TIP_multiSF, enabled=False, prefix=' (future) ') # this is always disabled. why?
            elem.normalise  = gui.comboBox(elem.normalise, ('to time', 'to monitor'), label = 'Normalization')
            elem.neutronWaveLen = gui.doubleSpinBox(elem.neutronWaveLen, minVal=0, decimals= 2, label=u'Neutron wavelength (\305)', tip=self.TIP_neutronWaveLen)

        gui.title('Crystal Structure', fullSize = False)
        elem.out = gui.comboBox(elem.out, ('Polycrystal/Amorphous', 'Single Crystal'), label=None, tip=self.TIP_rbnXYZ)
        with gui.indentation():
            if elem.out == elem.OUT_POLY_AMOR:
                with gui.hLayoutLabeled(label='Abscissa', preventHStretch=True):
                    elem.outAxisQ      = gui.checkBox(elem.outAxisQ, "q", tip=self.TIP_chkAxQ)
                    elem.outAxisD      = gui.checkBox(elem.outAxisD, "d", tip=self.TIP_chkAxD)
                    elem.outAxis2Theta = gui.checkBox(elem.outAxis2Theta, u"2\u0398", tip=self.TIP_chkAx2Theta)
                gui.helpBoxRight(self.check_abscissa(elem), style='error')
                elem.separation = gui.comboBox(elem.separation, ('XYZ', 'Coherent/Incoherent', 'No / none?'), label='Separation', tip=self.TIP_rbnXYZ)
            elif elem.out == elem.OUT_SINGLE_CRYST:
                elem.omegaOffset = gui.doubleSpinBox(elem.omegaOffset, decimals= 2, label='Omega Offset', tip=self.TIP_omegaOffset)
                
                elem.latticeSize = gui.vector(elem.latticeSize, ('a', 'b', 'c'), gui.doubleSpinBox, label=u'Lattice Size [\305]', minVal=0, decimals=4)
                angleLables = (u'\u03B1', u'\u03B2', u'\u03B3')
                elem.latticeAngles = gui.vector(elem.latticeAngles, angleLables, gui.doubleSpinBox, label=u'Lattice Angles [\u00B0]', minVal=5.0, maxVal=175.0, decimals=2)
                gui.helpBox(self.check_latticeAngles(elem), style='error')
                with gui.vLayoutLabeled(label='Scatter Plane', fullSize=False):
                    elem.scatterVectorU = gui.vector(elem.scatterVectorU, (), gui.doubleSpinBox, label='u', decimals=2)
                gui.helpBoxRight(self.check_scatterVectorU(elem), style='error')
                with gui.vLayoutLabeled(label=' ', fullSize=False):
                    elem.scatterVectorV = gui.vector(elem.scatterVectorV, (), gui.doubleSpinBox, label='v', decimals=2)
                gui.helpBoxRight(self.check_scatterVectorV(elem), style='error')

    def newDNSScriptElement(self):
        self.elem = DNSScriptElement()
        self.elem.reset()
        self.elem.facility_name   = self._settings.facility_name
        self.elem.instrument_name = self._settings.instrument_name

    def check_sampleDataPath(selfSelf, self):
        # path to sample data must exist
        if not os.path.lexists(self.sampleDataPath):
            return "sample data path not found"

    def check_filePrefixSuffix(selfSelf, self):
        # need prefix and suffix to find sample data
        if not self.filePrefix:
            return "missing sample data file prefix"

        if not self.fileSuffix:
            return "missing sample data file suffix"

    def check_dataRuns(selfSelf, self):
        # there must be data in the first row of the run data table
        if len(self.dataRuns) == 0:
            return "Missing sample data runs"

        # the must be a run in every row and a workspace name for every run
        for (runs, workspace, comment) in self.dataRuns:
            if not runs:
                return "All rows must contain run numbers"
            elif runs and not workspace:
                return "There must be a workspace to all run numbers"

    def check_maskAngles(selfSelf, self):
        """
        test the angles of mask detector table
        """
        for row, maskAngle in enumerate(self.maskAngles, start=1):
            (min_angle, max_angle) = maskAngle

            # set min or max angle if an angle is missing
            if not max_angle:
                max_angle = 180.0
            elif not min_angle:
                min_angle = 0.0

            for angle in (min_angle, max_angle):
                try:
                    float(angle)
                except ValueError as e:
                    return "'%s' is not a valid number (error in row %d)" % (angle, row)
                # angles must be bigger than 0.0 and lower than 180
                if float(angle) < 0.0 or float(angle) > 180.0:
                    return "Angle must be between 0.0 and 180.0 (error in row %d)" % row


            # all min angle must be lower than max angle
            if not float(min_angle) < float(max_angle):
                return "Min Angle must be smaller than max Angle (error in row %d)" % row

    def check_saveToFile(selfSelf, self):
        # if data should be saved to file output directory must be writeable and prefix must be given
        if self.saveToFile:
            if not os.path.lexists(self.outDir):
                return "output directory not found"
            elif not os.access(self.outDir, os.W_OK):
                self.error("cant write in directory "+str(self.outDir))

            if not self.outPrefix:
                return "missing output file prefix"

    def check_standardDataPath(selfSelf, self):
        #  path to standard data must exist
        if not os.path.lexists(self.standardDataPath):
            return "standard data path not found"

    def check_abscissa(selfSelf, self):
        # there must be at least selected one unit for x axis of the output workspace
        if self.out == self.OUT_POLY_AMOR and not self.outAxisQ and not self.outAxisD and not self.outAxis2Theta:
            return "no abscissa selected"

    def check_latticeAngles(selfSelf, self):
        # one angle of the lattice parameters angles cant be bigger than the other two added
        if self.out == self.OUT_SINGLE_CRYST:
            if self.latticeAngles[0] > self.latticeAngles[1] + self.latticeAngles[2] \
            or self.latticeAngles[1] > self.latticeAngles[0] + self.latticeAngles[2] \
            or self.latticeAngles[2] > self.latticeAngles[0] + self.latticeAngles[1]:
                return "Invalid lattice angles: one angle can't be bigger than the other to added"

    def check_scatterVectorU(selfSelf, self):
        # the scatter parameters can't all be zero
        if self.out == self.OUT_SINGLE_CRYST:
            if self.scatterVectorU[0] == 0.0 and self.scatterVectorU[1] == 0.0 and self.scatterVectorU[2] == 0.0:
                return "scatter vector cannot have a magnitude of zero"

    def check_scatterVectorV(selfSelf, self):
        # the scatter parameters can't all be zero
        if self.out == self.OUT_SINGLE_CRYST:
            if self.scatterVectorV[0] == 0.0 and self.scatterVectorV[1] == 0.0 and self.scatterVectorV[2] == 0.0:
                return "scatter vector cannot have a magnitude of zero"

    def get_state(self):
        """
        get the state of the ui
        :return: script element
        """
        return self.elem

    def set_state(self, dnsScriptElement):
        self.elem = dnsScriptElement
        self.gui.redrawGUI()