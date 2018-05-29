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

        gui.horizontalLayoutBegin()

        # left side:
        gui.verticalLayoutBegin()
        self._leftGUI()
        gui.verticalLayoutEnd()

        # right side:
        gui.verticalLayoutBegin()
        self._rightGUI()
        gui.verticalLayoutEnd()

        gui.horizontalLayoutEnd()
    
    def _leftGUI(self):
        elem = self.elem
        gui = self.gui

        gui.groupBoxBegin('Sample data')
        elem.sampleDataPath = gui.folderPathEdit(elem.sampleDataPath, title='Data Directory', tip=self.TIP_sampleDataPath)

        gui.horizontalLayoutBegin(title='File Prefix', tip=self.TIP_sampleFilePre)
        elem.filePrefix = gui.lineEdit(elem.filePrefix, tip=self.TIP_sampleFilePre)
        elem.fileSuffix = gui.lineEdit(elem.fileSuffix, title='suffix', tip=self.TIP_sampleFileSuff)
        gui.horizontalLayoutEnd()

        elem.dataRuns  = gui.dataTable(elem.dataRuns, ("Run numbers", "Output Workspace", "Comment"), tip=self.TIP_runsView)
        gui.groupBoxEnd()

        gui.groupBoxBegin('Mask Detectors')
        elem.maskAngles  = gui.dataTable(elem.maskAngles, (u"Min Angle[\305]", u"Max Angle[\305]"), tip=self.TIP_runsView)
        gui.groupBoxEnd()

        elem.saveToFile = \
        gui.groupBoxCheckedBegin(elem.saveToFile, title='Save to file')
        elem.outDir = gui.folderPathEdit(elem.outDir, title='Output Directory', tip=self.TIP_outDir)
        elem.outPrefix = gui.lineEdit(elem.outPrefix, title='Output File Prefix', tip=self.TIP_outFile)
        gui.groupBoxEnd()

    def _rightGUI(self):
        elem = self.elem
        gui = self.gui
        
        gui.groupBoxBegin('Standard Data')
        elem.standardDataPath = gui.folderPathEdit(elem.standardDataPath, title='Path', tip=self.TIP_standardDataPath)
        gui.groupBoxEnd()

        gui.groupBoxBegin('Data Reduction Settings')
        elem.detEffi   = gui.checkBox(elem.detEffi, title='Detector efficiency correction',               tip=self.TIP_chkDetEffi)
        gui.verticalLayoutBegin(isIndented=True)
        elem.sumVan    = gui.checkBox(elem.sumVan,  title='Sum Vanadium over detector position',          tip=self.TIP_chkSumVan, enabled=False)
        gui.verticalLayoutEnd(preventHStretch=True)

        elem.subInst   = gui.checkBox(elem.subInst, title='Subtract instrument background for sample', tip=self.TIP_chkSubInst)
        gui.verticalLayoutBegin(isIndented=True)
        elem.subFac    = gui.doubleSpinBox(elem.subFac, minVal=0, decimals= 2, title='Factor',                         tip=self.TIP_subFac,    enabled= elem.subInst)
        gui.verticalLayoutEnd(preventHStretch=True)

        elem.flipRatio = gui.checkBox(elem.flipRatio, title='Flipping ratio correction',  tip=self.TIP_chkFlipRatio)
        gui.verticalLayoutBegin(isIndented=True)
        elem.flipFac   = gui.doubleSpinBox(elem.flipFac, minVal=0, decimals= 2, title='Factor',                        tip=self.TIP_flipFac,   enabled=elem.flipRatio)
        gui.verticalLayoutEnd(preventHStretch=True)

        elem.multiSF        = gui.doubleSpinBox(elem.multiSF, minVal=0, maxVal=1, decimals= 2, title='Multiple SF scattering probability', tip=self.TIP_multiSF,   enabled=False) # this is always disabled. why?
        elem.normalise      = gui.radioButtonGroup(elem.normalise, ('time', 'monitor'), title = 'Normalization')
        elem.neutronWaveLen = gui.doubleSpinBox(elem.neutronWaveLen, minVal=0, decimals= 2, title=u'Neutron wavelength (\305)', tip=self.TIP_neutronWaveLen)
        gui.groupBoxEnd(preventHStretch=True)

        gui.groupBoxBegin('Crystal Structure')
        # sample type polycrystal/amorph
        if gui.radioButton(elem.out == elem.OUT_POLY_AMOR, title='Polycrystal/Amorphous', tip=self.TIP_rbnPolyAmor):
            elem.out = elem.OUT_POLY_AMOR
        gui.verticalLayoutBegin(isIndented = True, enabled=elem.out == elem.OUT_POLY_AMOR)
        gui.horizontalLayoutBegin(title='Abscissa')
        elem.outAxisQ      = gui.checkBox(elem.outAxisQ, "q", tip=self.TIP_chkAxQ)
        elem.outAxisD      = gui.checkBox(elem.outAxisD, "d", tip=self.TIP_chkAxD)
        elem.outAxis2Theta = gui.checkBox(elem.outAxis2Theta, u"2\u0398", tip=self.TIP_chkAx2Theta)
        gui.horizontalLayoutEnd(preventHStretch=True)
        elem.separation  = gui.radioButtonGroup(elem.separation, ('XYZ', 'Coherent/Incoherent', 'No / none?'), title='Separation', tip=self.TIP_rbnXYZ)
        gui.verticalLayoutEnd(preventVStretch=True)

        # sample type singlecrystal
        if gui.radioButton(elem.out == elem.OUT_SINGLE_CRYST, title='Single Crystal', tip=self.TIP_rbnSingleCryst):
            elem.out = elem.OUT_SINGLE_CRYST
        gui.verticalLayoutBegin(isIndented = True, enabled=elem.out == elem.OUT_SINGLE_CRYST)
        elem.omegaOffset = gui.doubleSpinBox(elem.omegaOffset, decimals= 2, title='Omega Offset', tip=self.TIP_omegaOffset)
        gui.horizontalLayoutBegin(title='Lattice Parameters')
        elem.latticeA = gui.doubleSpinBox(elem.latticeA, minVal=0, decimals=4, title=u'a[\305]', tip=self.TIP_latticeA)
        elem.latticeB = gui.doubleSpinBox(elem.latticeB, minVal=0, decimals=4, title=u'b[\305]', tip=self.TIP_latticeB)
        elem.latticeC = gui.doubleSpinBox(elem.latticeC, minVal=0, decimals=4, title=u'c[\305]', tip=self.TIP_latticeC)
        gui.horizontalLayoutEnd()
        gui.horizontalLayoutBegin(title=' ')
        elem.latticeAlpha = gui.doubleSpinBox(elem.latticeAlpha, minVal=5.0, maxVal=175.0, decimals= 2, title=u'\u03B1[\u00B0]', tip=self.TIP_latticeAlpha)
        elem.latticeBeta  = gui.doubleSpinBox(elem.latticeBeta , minVal=5.0, maxVal=175.0, decimals= 2, title=u'\u03B2[\u00B0]', tip=self.TIP_latticeBeta)
        elem.latticeGamma = gui.doubleSpinBox(elem.latticeGamma, minVal=5.0, maxVal=175.0, decimals= 2, title=u'\u03B3[\u00B0]', tip=self.TIP_latticeGamma)
        gui.horizontalLayoutEnd()
        gui.horizontalLayoutBegin(title='Scatter Plane')
        elem.scatterU1 = gui.doubleSpinBox(elem.scatterU1, decimals= 2, title='u', tip=self.TIP_scatterU1)
        elem.scatterU2 = gui.doubleSpinBox(elem.scatterU2, decimals= 2, tip=self.TIP_scatterU2)
        elem.scatterU3 = gui.doubleSpinBox(elem.scatterU3, decimals= 2, tip=self.TIP_scatterU3)
        gui.horizontalLayoutEnd()
        gui.horizontalLayoutBegin(title=' ')
        elem.scatterV1 = gui.doubleSpinBox(elem.scatterV1, decimals= 2, title='v', tip=self.TIP_scatterV1)
        elem.scatterV2 = gui.doubleSpinBox(elem.scatterV2, decimals= 2, tip=self.TIP_scatterV2)
        elem.scatterV3 = gui.doubleSpinBox(elem.scatterV3, decimals= 2, tip=self.TIP_scatterV3)
        gui.horizontalLayoutEnd()
        gui.verticalLayoutEnd(preventVStretch=True)
        gui.groupBoxEnd(preventVStretch=True)
              
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
        self.gui.redrawGUI()