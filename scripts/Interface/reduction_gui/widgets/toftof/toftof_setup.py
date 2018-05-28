#pylint: disable = too-many-instance-attributes, too-many-branches, too-many-public-methods
#pylint: disable = W0622
"""
TOFTOF reduction workflow gui.
"""
from __future__ import (absolute_import, division, print_function)
from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets  import *
from PyQt5 import QtWidgets, QtCore

from reduction_gui.widgets.base_widget import BaseWidget
from reduction_gui.reduction.toftof.toftof_reduction import TOFTOFScriptElement

from functionalStyleGUI import FunctionalStyleGUI
#-------------------------------------------------------------------------------


class TOFTOFSetupWidget(BaseWidget):
    ''' The one and only tab page. '''
    name = 'TOFTOF Reduction'

    # tooltips
    TIP_prefix  = ''
    TIP_dataDir = ''
    TIP_saveDir = ''

    TIP_vanRuns = ''
    TIP_vanCmnt = ''

    TIP_ecRuns = ''
    TIP_ecFactor = ''

    TIP_binEon = ''
    TIP_binEstart = ''
    TIP_binEstep = ''
    TIP_binEend = ''

    TIP_binQon = ''
    TIP_binQstart = ''
    TIP_binQstep = ''
    TIP_binQend = ''

    TIP_maskDetectors = ''

    TIP_dataRunsView = ''

    TIP_chkSubtractECVan = ''
    TIP_chkReplaceNaNs = 'Replace NaNs with 0'
    TIP_chkCreateDiff = ''
    TIP_chkKeepSteps = ''

    TIP_chkSofQW = ''
    TIP_chkSofTW = ''
    TIP_chkNxspe = 'Save for MSlice'
    TIP_chkNexus = 'Save for Mantid'
    TIP_chkAscii = 'Will be available soon'

    TIP_rbtNormaliseNone = ''
    TIP_rbtNormaliseMonitor = ''
    TIP_rbtNormaliseTime = ''

    TIP_rbtCorrectTOFNone = ''
    TIP_rbtCorrectTOFVan = ''
    TIP_rbtCorrectTOFSample = ''

    def __init__(self, settings):
        BaseWidget.__init__(self, settings = settings)
        self.newTOFTOFScriptElement()
        #GUI
        self.gui = FunctionalStyleGUI(self, self.OnGUI)
        self.gui.redrawGUI()

    def newTOFTOFScriptElement(self):
        self.elem = TOFTOFScriptElement()
        self.elem.reset()
        self.elem.facility_name   = self._settings.facility_name
        self.elem.instrument_name = self._settings.instrument_name

    def OnGUI(self):
        if self.elem == None:
            self.newTOFTOFScriptElement()

        def line_text(lineEdit):
            return lineEdit.text().strip()

        elem = self.elem
        gui = self.gui

        gui.horizontalLayoutBegin()

        # left side:
        gui.verticalLayoutBegin()
        self._leftGUI()
        gui.verticalLayoutEnd(preventVStretch = True)

        # right side:
        gui.verticalLayoutBegin()
        self._rightGUI()
        gui.verticalLayoutEnd()

        gui.horizontalLayoutEnd()
    
    def _leftGUI(self):
        elem = self.elem
        gui = self.gui
        
        gui.groupBoxHBegin('Data search directory')
        elem.dataDir       = gui.folderPathEdit(elem.dataDir, title='Search Directory', tip=self.TIP_dataDir)
        gui.groupBoxHEnd()

        gui.groupBoxBegin('Inputs')
        elem.vanRuns       = gui.lineEdit(elem.vanRuns, title='Vanadium Runs', tip=self.TIP_vanRuns)
        elem.vanCmnt       = gui.lineEdit(elem.vanCmnt, title='Van. comment', tip=self.TIP_vanCmnt)

        gui.horizontalLayoutBegin(title='Empty can runs', tip=self.TIP_ecRuns)
        elem.ecRuns        = gui.lineEdit(elem.ecRuns, tip=self.TIP_ecRuns)
        elem.ecFactor      = gui.doubleSpinBox(elem.ecFactor, 0, 1, title='EC factor', tip=self.TIP_ecFactor)
        gui.horizontalLayoutEnd()

        elem.maskDetectors = gui.lineEdit(elem.maskDetectors, title='Mask Detectors', tip=self.TIP_maskDetectors)
        gui.groupBoxEnd()

        gui.groupBoxBegin('Binning')
        gui.horizontalLayoutBegin(title=" ")
        gui.label(text='Start', tip=self.TIP_binEstart)
        gui.label(text='Step',  tip=self.TIP_binEstep)
        gui.label(text='End',   tip=self.TIP_binEend)
        gui.horizontalLayoutEnd()

        elem.binEon = \
        gui.horizontalLayoutCheckedBegin(elem.binEon, "Energy", tip=self.TIP_binEon)
        elem.binEstart = gui.doubleSpinBox(elem.binEstart,              tip=self.TIP_binEstart, enabled=elem.binEon)
        elem.binEstep  = gui.doubleSpinBox(elem.binEstep, decimals = 4, tip=self.TIP_binEstep, enabled=elem.binEon)
        elem.binEend   = gui.doubleSpinBox(elem.binEend,                tip=self.TIP_binEend, enabled=elem.binEon)
        gui.horizontalLayoutEnd()

        if not elem.binEon:
            elem.binQon = False
        elem.binQon = \
        gui.horizontalLayoutCheckedBegin(elem.binQon, "Q", tip=self.TIP_binQon, enabled=elem.binEon)
        elem.binQstart = gui.doubleSpinBox(elem.binQstart, title=None, tip=self.TIP_binQstart, enabled=elem.binQon)
        elem.binQstep  = gui.doubleSpinBox(elem.binQstep,  title=None, tip=self.TIP_binQstep, enabled=elem.binQon)
        elem.binQend   = gui.doubleSpinBox(elem.binQend,   title=None, tip=self.TIP_binQend, enabled=elem.binQon)
        gui.horizontalLayoutEnd()
        gui.groupBoxEnd()


        gui.groupBoxBegin('Options')
        elem.subtractECVan = gui.checkBox(elem.subtractECVan, 'Subtract empty can from vanadium' , tip=self.TIP_chkSubtractECVan)
        elem.normalise     = gui.radioButtonGroup(elem.normalise, ('none', 'to monitor', 'to time'), title='Normalize')
        elem.correctTof    = gui.radioButtonGroup(elem.correctTof, ('none', 'vanadium', 'sample'), title='Correct TOF')

        elem.replaceNaNs = gui.checkBox(elem.replaceNaNs, 'Replace special values in S(Q,W) with 0', tip=self.TIP_chkReplaceNaNs, enabled=elem.binQon)
        elem.createDiff  = gui.checkBox(elem.createDiff,  'Create diffractograms'                  , tip=self.TIP_chkCreateDiff, enabled=elem.binEon)
        elem.keepSteps   = gui.checkBox(elem.keepSteps,   'Keep intermediate steps'                , tip=self.TIP_chkKeepSteps)
        gui.groupBoxEnd()

    def _rightGUI(self):
        elem = self.elem
        gui = self.gui
        
        gui.groupBoxBegin('Workspace prefix')
        elem.prefix = gui.lineEdit(elem.prefix,  title='Prefix', tip=self.TIP_prefix)
        gui.groupBoxEnd()

        gui.groupBoxBegin('Data')
        print('elem.dataRuns = ', elem.dataRuns)
        elem.dataRuns  = gui.dataTable(elem.dataRuns, ('Data runs', 'Comment'), tip=self.TIP_dataRunsView)
        print('elem.dataRuns = ', elem.dataRuns)
        gui.groupBoxEnd()
        #layout = self.gui.currentLayout()
        #layout.setRowStretch(layout.rowCount()-1, 5)

        gui.groupBoxBegin('Save Reduced Data')
        elem.saveDir       = gui.folderPathEdit(elem.saveDir, title='Save Directory', tip=self.TIP_saveDir)

        gui.horizontalLayoutBegin(title='Workspaces')
        elem.saveSofQW = gui.checkBox(elem.saveSofQW, 'S(Q,W)'     , tip=self.TIP_chkSofQW, enabled=elem.binQon)
        elem.saveSofTW = gui.checkBox(elem.saveSofTW, 'S(2theta,W)', tip=self.TIP_chkSofTW)
        gui.horizontalLayoutEnd()

        gui.horizontalLayoutBegin(title='Format')

        #if not elem.binEon:
        #    elem.saveNXSPE = False
        
        elem.saveNXSPE = gui.checkBox(elem.saveNXSPE, 'NXSPE', tip=self.TIP_chkNxspe, enabled=elem.binEon)
        elem.saveNexus = gui.checkBox(elem.saveNexus, 'NeXus', tip=self.TIP_chkNexus)
        # disable save Ascii, it is not available for the moment
        elem.saveAscii = gui.checkBox(elem.saveAscii, 'Ascii', tip=self.TIP_chkAscii, enabled=False)
        gui.horizontalLayoutEnd()
        gui.groupBoxEnd()


    def get_state(self):
        return self.elem
        elem = TOFTOFScriptElement()

        def line_text(lineEdit):
            return lineEdit.text().strip()

    def set_state(self, toftofScriptElement):
        self.elem = toftofScriptElement
        self.gui.redrawGUI()

#-------------------------------------------------------------------------------
# eof
