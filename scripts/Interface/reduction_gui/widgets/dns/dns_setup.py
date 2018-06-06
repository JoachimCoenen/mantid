from PyQt5.QtWidgets import QLineEdit, QPushButton, QTableView, QHeaderView, QCheckBox, QDoubleSpinBox, QRadioButton, \
    QLayout, QWidget, QSpacerItem, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QGroupBox, QGridLayout, QButtonGroup, \
    QSizePolicy, QMessageBox, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, QModelIndex, Qt
from PyQt5 import QtWidgets, QtCore, QtGui

from reduction_gui.widgets.base_widget import BaseWidget
from reduction_gui.reduction.dns.dns_reduction import DNSScriptElement

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
        self.gui = FunctionalStyleGUI(self, self.OnGUI)
        self.gui.redrawGUI()
        return

    def OnGUI(self):
        if self.elem == None:
            self.newDNSScriptElement()
        gui = self.gui
        elem = self.elem

        with gui.hLayout():
            with gui.vLayout():
                self._leftGUI()
            with gui.vLayout(preventVStretch = True):
                self._rightGUI()
        return

    def _leftGUI(self):
        elem = self.elem
        gui = self.gui

        with gui.groupBox('Sample data'):
            elem.sampleDataPath = gui.folderPathEdit(elem.sampleDataPath, label='Data Directory', tip=self.TIP_sampleDataPath)
            with gui.hLayoutLabeled(label='File Prefix', tip=self.TIP_sampleFilePre):
                elem.filePrefix = gui.lineEdit(elem.filePrefix, tip=self.TIP_sampleFilePre)
                elem.fileSuffix = gui.lineEdit(elem.fileSuffix, label='suffix', tip=self.TIP_sampleFileSuff)

            elem.dataRuns  = gui.dataTable(elem.dataRuns, ("Run numbers", "Output Workspace", "Comment"), tip=self.TIP_runsView)

        with gui.groupBox('Mask Detectors'):
            elem.maskAngles  = gui.dataTable(elem.maskAngles, (u"Min Angle[\305]", u"Max Angle[\305]"), tip=self.TIP_runsView)

        with gui.groupBoxChecked(elem.saveToFile, title='Save to file') as elem.saveToFile:
            elem.outDir = gui.folderPathEdit(elem.outDir, label='Output Directory', tip=self.TIP_outDir, enabled=elem.saveToFile)
            elem.outPrefix = gui.lineEdit(elem.outPrefix, label='Output File Prefix', tip=self.TIP_outFile, enabled=elem.saveToFile)

    def _rightGUI(self):
        elem = self.elem
        gui = self.gui
        
        with gui.groupBox('Standard Data'):
            elem.standardDataPath = gui.folderPathEdit(elem.standardDataPath, label='Path', tip=self.TIP_standardDataPath)

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

            gui.addSpacer(30 * 1, QtWidgets.QSizePolicy.Fixed)
            elem.out = gui.comboBox(elem.out, ('Polycrystal/Amorphous', 'Single Crystal'), label='Crystal Structure', tip=self.TIP_rbnXYZ)
            with gui.indentation():
                if elem.out == elem.OUT_POLY_AMOR:
                    with gui.hLayoutLabeled(label='Abscissa', preventHStretch=True):
                        elem.outAxisQ      = gui.checkBox(elem.outAxisQ, "q", tip=self.TIP_chkAxQ)
                        elem.outAxisD      = gui.checkBox(elem.outAxisD, "d", tip=self.TIP_chkAxD)
                        elem.outAxis2Theta = gui.checkBox(elem.outAxis2Theta, u"2\u0398", tip=self.TIP_chkAx2Theta)
                    elem.separation = gui.comboBox(elem.separation, ('XYZ', 'Coherent/Incoherent', 'No / none?'), label='Separation', tip=self.TIP_rbnXYZ)
                elif elem.out == elem.OUT_SINGLE_CRYST:
                    elem.omegaOffset = gui.doubleSpinBox(elem.omegaOffset, decimals= 2, label='Omega Offset', tip=self.TIP_omegaOffset)
                    
                    with gui.hLayoutLabeled(label=u'Lattice Size [\305]', fullSize=False, isIndented=False):
                        elem.latticeA = gui.doubleSpinBox(elem.latticeA, minVal=0, decimals=4, label='a', tip=self.TIP_latticeA)
                        elem.latticeB = gui.doubleSpinBox(elem.latticeB, minVal=0, decimals=4, label='b', tip=self.TIP_latticeB)
                        elem.latticeC = gui.doubleSpinBox(elem.latticeC, minVal=0, decimals=4, label='c', tip=self.TIP_latticeC)
                    with gui.hLayoutLabeled(label=u'Lattice Angles [\u00B0]', fullSize=False, isIndented=False):
                        elem.latticeAlpha = gui.doubleSpinBox(elem.latticeAlpha, minVal=5.0, maxVal=175.0, decimals= 2, label=u'\u03B1', tip=self.TIP_latticeAlpha)
                        elem.latticeBeta  = gui.doubleSpinBox(elem.latticeBeta , minVal=5.0, maxVal=175.0, decimals= 2, label=u'\u03B2', tip=self.TIP_latticeBeta)
                        elem.latticeGamma = gui.doubleSpinBox(elem.latticeGamma, minVal=5.0, maxVal=175.0, decimals= 2, label=u'\u03B3', tip=self.TIP_latticeGamma)
                    with gui.vLayoutLabeled(label='Scatter Plane', fullSize=False):
                        with gui.hLayoutLabeled(label='u', fullSize=False):
                            elem.scatterU1 = gui.doubleSpinBox(elem.scatterU1, decimals= 2, tip=self.TIP_scatterU1)
                            elem.scatterU2 = gui.doubleSpinBox(elem.scatterU2, decimals= 2, tip=self.TIP_scatterU2)
                            elem.scatterU3 = gui.doubleSpinBox(elem.scatterU3, decimals= 2, tip=self.TIP_scatterU3)
                    with gui.vLayoutLabeled(label=' ', fullSize=False):
                        with gui.hLayoutLabeled(label='v', fullSize=False):
                            elem.scatterV1 = gui.doubleSpinBox(elem.scatterV1, decimals= 2, tip=self.TIP_scatterV1)
                            elem.scatterV2 = gui.doubleSpinBox(elem.scatterV2, decimals= 2, tip=self.TIP_scatterV2)
                            elem.scatterV3 = gui.doubleSpinBox(elem.scatterV3, decimals= 2, tip=self.TIP_scatterV3)
            
    def newDNSScriptElement(self):
        self.elem = DNSScriptElement()
        self.elem.reset()
        self.elem.facility_name   = self._settings.facility_name
        self.elem.instrument_name = self._settings.instrument_name

    def get_state(self):
        """
        get the state of the ui
        :return: script element
        """
        return self.elem

    def set_state(self, dnsScriptElement):
        self.elem = dnsScriptElement
        #self.gui.redrawGUI()