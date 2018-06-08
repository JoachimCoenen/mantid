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
import re

from reduction_gui.widgets.base_widget import BaseWidget
from reduction_gui.reduction.toftof.toftof_reduction import TOFTOFScriptElement

from functionalStyleGUI import FunctionalStyleGUI
#-------------------------------------------------------------------------------

class Mydict(object):
    """docstring for Mydict"""
    def __init__(self):
        super(Mydict, self).__init__()
        self.__dict__ = {'hi': 5, 'apple': 'hello'}
            

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
        self.myDict = Mydict()
        self._recDepth = 0
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

        elem = self.elem
        gui = self.gui

        with gui.splitter():
            with gui.vLayout(preventVStretch = True):
                self._leftGUI()
            with gui.vLayout():
                self._rightGUI()

    def _leftGUI(self):
        elem = self.elem
        gui = self.gui
        
        with gui.groupBox('Data search directory'):
            elem.dataDir       = gui.folderPathEdit(elem.dataDir, label='Search Directory', tip=self.TIP_dataDir)
        #
        with gui.groupBox('Inputs'):
            elem.vanRuns, errStr = gui.runsEdit(elem.vanRuns, label='Vanadium Runs', tip=self.TIP_vanRuns)
            gui.helpBoxRight(errStr, style='error')
            elem.vanCmnt       = gui.lineEdit(elem.vanCmnt, label='Van. comment', tip=self.TIP_vanCmnt)
            self.validate_vanCmnt(elem)
            with gui.hLayoutLabeled(label='Empty can runs', tip=self.TIP_ecRuns):
                elem.ecRuns, errStr = gui.runsEdit(elem.ecRuns, tip=self.TIP_ecRuns)
                elem.ecFactor      = gui.doubleSpinBox(elem.ecFactor, 0, 1, label='EC factor', tip=self.TIP_ecFactor)
            gui.helpBoxRight(errStr, style='error')
            elem.maskDetectors, errStr = gui.runsEdit(elem.maskDetectors, label='Mask Detectors', tip=self.TIP_maskDetectors)
            gui.helpBoxRight(errStr, style='error')
        
        with gui.groupBox('Binning'):
            with gui.hLayoutLabeled(label=" "):
                gui.label(text='Start', toolTip=self.TIP_binEstart)
                gui.label(text='Step',  toolTip=self.TIP_binEstep)
                gui.label(text='End',   toolTip=self.TIP_binEend)
            with gui.hLayoutChecked(elem.binEon, "Energy", tip=self.TIP_binEon) as elem.binEon:
                elem.binEstart = gui.doubleSpinBox(elem.binEstart,              tip=self.TIP_binEstart, enabled=elem.binEon)
                elem.binEstep  = gui.doubleSpinBox(elem.binEstep, decimals = 4, tip=self.TIP_binEstep, enabled=elem.binEon)
                elem.binEend   = gui.doubleSpinBox(elem.binEend,                tip=self.TIP_binEend, enabled=elem.binEon)
            self.validate_binEon(elem)
            if not elem.binEon:
                elem.binQon = False
            with gui.hLayoutChecked(elem.binQon, "Q", tip=self.TIP_binQon, enabled=elem.binEon) as elem.binQon:
                elem.binQstart = gui.doubleSpinBox(elem.binQstart, tip=self.TIP_binQstart, enabled=elem.binQon)
                elem.binQstep  = gui.doubleSpinBox(elem.binQstep,  tip=self.TIP_binQstep, enabled=elem.binQon)
                elem.binQend   = gui.doubleSpinBox(elem.binQend,   tip=self.TIP_binQend, enabled=elem.binQon)
            self.validate_binQon(elem)

        with gui.groupBox('Options'):
            elem.subtractECVan = gui.checkBox(elem.subtractECVan, 'Subtract empty can from vanadium' , tip=self.TIP_chkSubtractECVan)
            self.validate_subtractECVan(elem)
            elem.normalise     = gui.comboBox(elem.normalise, ('none', 'to monitor', 'to time'), label='Normalize')
            elem.correctTof    = gui.comboBox(elem.correctTof, ('none', 'vanadium', 'sample'), label='Correct TOF')
            self.validate_correctTof(elem)
            #
            elem.replaceNaNs = gui.checkBox(elem.replaceNaNs, 'Replace special values in S(Q,W) with 0', tip=self.TIP_chkReplaceNaNs, enabled=elem.binQon)
            elem.createDiff  = gui.checkBox(elem.createDiff,  'Create diffractograms'                  , tip=self.TIP_chkCreateDiff, enabled=elem.binEon)
            elem.keepSteps   = gui.checkBox(elem.keepSteps,   'Keep intermediate steps'                , tip=self.TIP_chkKeepSteps)

    def _rightGUI(self):
        elem = self.elem
        gui = self.gui
        
        with gui.groupBox('Workspace prefix'):
            elem.prefix = gui.lineEdit(elem.prefix,  label='Prefix', tip=self.TIP_prefix)
            elem.prefix = gui.lineEdit(elem.prefix,  label='Prefix', tip=self.TIP_prefix)

        with gui.groupBox('Data'):
            elem.dataRuns  = gui.dataTable(elem.dataRuns, ('Data runs', 'Comment'), tip=self.TIP_dataRunsView)
            gui.helpBox(self.validate_dataRuns(elem), style='error')
        #layout = self.gui.currentLayout()
        #layout.setRowStretch(layout.rowCount()-1, 5)

        with gui.groupBox('Save Reduced Data'):
            elem.saveDir       = gui.folderPathEdit(elem.saveDir, label='Save Directory', tip=self.TIP_saveDir)

            with gui.hLayoutLabeled(label='Workspaces'):
                elem.saveSofQW = gui.checkBox(elem.saveSofQW, 'S(Q,W)'     , tip=self.TIP_chkSofQW, enabled=elem.binQon)
                elem.saveSofTW = gui.checkBox(elem.saveSofTW, 'S(2theta,W)', tip=self.TIP_chkSofTW)

            with gui.hLayoutLabeled(label='Format'):
                #if not elem.binEon:
                #    elem.saveNXSPE = False
                elem.saveNXSPE = gui.checkBox(elem.saveNXSPE, 'NXSPE', tip=self.TIP_chkNxspe, enabled=elem.binEon)
                elem.saveNexus = gui.checkBox(elem.saveNexus, 'NeXus', tip=self.TIP_chkNexus)
                # disable save Ascii, it is not available for the moment
                elem.saveAscii = gui.checkBox(elem.saveAscii, 'Ascii', tip=self.TIP_chkAscii, enabled=False)
            self.validate_savingSettings(elem)


    def validate_correctTof(self, elem):
        # must have vanadium for TOF correction
        if elem.CORR_TOF_VAN == elem.correctTof:
            if not elem.vanRuns:
                self.gui.helpBox('missing vanadium runs', style='error')

    def validate_subtractECVan(self, elem):
        # must have vanadium and empty can for subtracting EC from van
        if elem.subtractECVan:
            if not elem.vanRuns:
                self.gui.helpBox('missing vanadium runs', style='error')
            if not elem.ecRuns:
                self.gui.helpBox('missing empty can runs', style='error')

    def validate_binEon(self, elem):
        if elem.binEon:
            self.validate_binParams(elem.binEstart, elem.binEstep, elem.binEend)

    def validate_binQon(self, elem):
        if elem.binQon:
            self.validate_binParams(elem.binQstart, elem.binQstep, elem.binQend)

    def validate_binParams(self, start, step, end):
        if not (start < end and step > 0 and start + step <= end):
            self.gui.helpBoxRight('incorrect binning parameters', style='error')

    def validate_dataRuns(self, elem):
        # must have some data runs
        if not elem.dataRuns:
            self.gui.helpBox('missing data runs', style='error')
        else:
            for row, run in enumerate(elem.dataRuns, start=1):
                errorStr = self.gui.validate_runs(run[0])
                if errorStr:
                    return '%s in row %d' % (errorStr, row)

    def validate_vanCmnt(self, elem):
        # must have a comment for vanadium runs
        if elem.vanRuns and not elem.vanCmnt:
            self.gui.helpBox('missing vanadium comment', style='error')

    def validate_savingSettings(self, elem):
        # saving settings must be consistent
        if elem.saveNXSPE or elem.saveNexus or elem.saveAscii:
            if not elem.saveDir:
                self.gui.helpBox('missing directory to save the data', style='error')
            elif not (elem.saveSofQW or elem.saveSofTW):
                self.gui.helpBox('you must select workspaces to save', style='error')
        elif elem.saveSofQW or elem.saveSofTW:
            if not elem.saveDir:
                self.gui.helpBox('missing directory to save the data', style='error')
            self.gui.helpBox('missing data format to save', style='error')

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
