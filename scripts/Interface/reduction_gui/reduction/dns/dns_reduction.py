import xml.dom.minidom

from collections import OrderedDict
import os
import re

from reduction_gui.reduction.scripter import BaseScriptElement, BaseReductionScripter
import mantid.simpleapi as api


class DNSScriptElement(BaseScriptElement):

    # normalization
    NORM_TIME = 0
    NORM_MONITOR = 1

    OUT_POLY_AMOR = 0
    OUT_SINGLE_CRYST = 1

    # separation
    SEP_XYZ = 0
    SEP_COH = 1
    SEP_NO = 2

    DEF_SaveToFile = False

    DEF_DetEffi = True
    DEF_SumVan = False
    DEF_SubInst = True
    DEF_SubFac = 1.0
    DEF_FlippRatio = True
    DEF_FlippFac = 1.0
    DEF_MultiSF = 0.0
    DEF_Normalise = NORM_TIME
    DEF_NeutWaveLen = 0.0
    #DEF_Intermediate = False

    DEF_Output = OUT_POLY_AMOR

    DEF_OutAxisQ = True
    DEF_OutAxisD = True
    DEF_OutAxis2Theta = True
    DEF_Separation = SEP_XYZ

    DEF_OmegaOffset = 0.0
    DEF_LatticeA = 0.0
    DEF_LatticeB = 0.0
    DEF_LatticeC = 0.0
    DEF_LatticeAlpha = 0.0
    DEF_LatticeBeta = 0.0
    DEF_LatticeGamma = 0.0
    DEF_ScatterU1 = 0.0
    DEF_ScatterU2 = 0.0
    DEF_ScatterU3 = 0.0
    DEF_ScatterV1 = 0.0
    DEF_ScatterV2 = 0.0
    DEF_ScatterV3 = 0.0

    XML_TAG = 'DNSReduction'

    def reset(self):

        self.facility_name = ''
        self.instrument_name = ''

        self.sampleDataPath = ''
        self.filePrefix = ''
        self.fileSuffix = ''

        self.dataRuns = []

        self.maskAngles = []

        self.saveToFile = self.DEF_SaveToFile
        self.outDir = ''
        self.outPrefix = ''

        self.standardDataPath = ''

        self.detEffi = self.DEF_DetEffi
        self.sumVan = self.DEF_SumVan
        self.subInst = self.DEF_SubInst
        self.subFac = self.DEF_SubFac
        self.flippRatio = self.DEF_FlippRatio
        self.flippFac = self.DEF_FlippFac
        self.multiSF = self.DEF_MultiSF
        self.normalise = self.DEF_Normalise
        self.neutronWaveLen = self.DEF_NeutWaveLen

        self.out = self.DEF_Output

        self.outAxisQ = self.DEF_OutAxisQ
        self.outAxisD = self.DEF_OutAxisD
        self.outAxis2Theta = self.DEF_OutAxis2Theta
        self.separation = self.DEF_Separation

        self.omegaOffset = self.DEF_OmegaOffset
        self.latticeA = self.DEF_LatticeA
        self.latticeB = self.DEF_LatticeB
        self.latticeC = self.DEF_LatticeC
        self.latticeAlpha = self.DEF_LatticeAlpha
        self.latticeBeta = self.DEF_LatticeBeta
        self.latticeGamma = self.DEF_LatticeGamma
        self.scatterU1 = self.DEF_ScatterU1
        self.scatterU2 = self.DEF_ScatterU2
        self.scatterU3 = self.DEF_ScatterU3
        self.scatterV1 = self.DEF_ScatterV1
        self.scatterV2 = self.DEF_ScatterV2
        self.scatterV3 = self.DEF_ScatterV3

    def to_xml(self):

        res =['']

        def put(tag, val):
            res[0] += ' <{0}>{1}</{0}>\n'.format(tag, str(val))

        put('sample_data_path', self.sampleDataPath)
        put('file_prefix',      self.filePrefix)
        put('file_suffix',      self.fileSuffix)

        for (runs, ws, cmnt) in self.dataRuns:
            put('data_runs',             runs)
            put('data_output_workspace', ws)
            put('data_comment',          cmnt)

        for (min, max) in self.maskAngles:
            put('mask_min_Angle', min)
            put('mask_max_Angle', max)

        put('save_to_file',       self.saveToFile)
        put('output_directory',   self.outDir)
        put('output_file_prefix', self.outPrefix)

        put('standard_data_path', self.standardDataPath)

        put('detector_efficiency',        self.detEffi)
        put('sum_Vanadium',               self.sumVan)
        put('subtract_instrument',        self.subInst)
        put('subtract_instrument_factor', self.subFac)
        put('flipping_ratio',             self.flippRatio)
        put('flipping_ratio_factor',      self.flippFac)
        put('multiple_SF_scattering',     self.multiSF)
        put('normalise',                  self.normalise)
        put('neutron_wave_length',        self.neutronWaveLen)

        put('output',             self.out)

        put('output_Axis_q',      self.outAxisQ)
        put('output_Axis_d',      self.outAxisD)
        put('output_Axis_2Theta', self.outAxis2Theta)
        put('separation',         self.separation)

        put('lattice_parameters_a',     self.latticeA)
        put('lattice_parameters_b',     self.latticeB)
        put('lattice_patameters_c',     self.latticeC)
        put('lattice_patameters_alpha', self.latticeAlpha)
        put('lattice_parameters_beta',  self.latticeBeta)
        put('lattice_parameters_gamma', self.latticeGamma)
        put('scattering_Plane_u_1',     self.scatterU1)
        put('scattering_Plane_u_2',     self.scatterU2)
        put('scattering_Plane_u_3',     self.scatterU3)
        put('scattering_Plane_v_1',     self.scatterV1)
        put('scattering_Plane_v_2',     self.scatterV2)
        put('scattering_Plane_v_3',     self.scatterV3)

        return '<{0}>\n{1}</{0}>\n'.format(self.XML_TAG, res[0])

    def from_xml(self, xmlStr):

        self.reset()

        dom = xml.dom.minidom.parseString(xmlStr)
        els = dom.getElementsByTagName(self.XML_TAG)

        if els:

            dom = els[0]

            def get_str(tag, default=''):
                return BaseScriptElement.getStringElement(dom, tag, default=default)

            def get_int(tag, default):
                return BaseScriptElement.getIntElement(dom, tag, default=default)

            def get_flt(tag, default):
                return BaseScriptElement.getFloatElement(dom, tag, default=default)

            def get_strlst(tag):
                return BaseScriptElement.getStringList(dom, tag)

            def get_bol(tag, default):
                return BaseScriptElement.getBoolElement(dom, tag, default=default)

            self.sampleDataPath = get_str('sample_data_path')
            self.filePrefix = get_str('file_prefix')
            self.fileSuffix = get_str('file_suffix')

            dataRuns = get_strlst('data_runs')
            dataOutWs = get_strlst('data_output_workspace')
            dataCmts = get_strlst('data_comment')

            for i in range(min(len(dataRuns), len(dataOutWs), len(dataCmts))):
                self.dataRuns.append((dataRuns[i], dataOutWs[i], dataCmts[i]))

            maskMin = get_strlst('mask_min_Angle')
            maskMax = get_strlst('mask_max_Angle')

            for i in range(min(len(maskMin), len(maskMax))):
                self.maskAngles.append((maskMin[i], maskMax[i]))

            self.saveToFile = get_bol('save_to_file', self.DEF_SaveToFile)
            self.outDir = get_str('output_directory')
            self.outPrefix = get_str('output_file_prefix')

            self.standardDataPath = get_str('standard_data_path')

            self.detEffi = get_bol('detector_efficiency', self.DEF_DetEffi)
            self.sumVan = get_bol('sum_Vanadium', self.DEF_SumVan)
            self.subInst = get_bol('subtract_instrument', self.DEF_SubInst)
            self.subFac = get_flt('subtract_instrument_factor', self.subFac)
            self.flippRatio = get_bol('flipping_ratio', self.DEF_FlippRatio)
            self.multiSF = get_flt('multiple_SF_scattering', self.DEF_MultiSF)
            self.normalise = get_int('normalise', self.DEF_Normalise)
            self.neutronWaveLen = get_flt('neutron_wave_length', self.DEF_NeutWaveLen)

            self.out = get_int('output', self.DEF_Output)

            self.outAxisQ = get_bol('output_Axis_q', self.DEF_OutAxisQ)
            self.outAxisD = get_bol('output_Axis_d', self.DEF_OutAxisD)
            self.outAxis2Theta = get_bol('output_Axis_2Theta', self.DEF_OutAxis2Theta)
            self.separation = get_int('separation', self.DEF_Separation)

            self.latticeA = get_flt('lattice_parameters_a', self.DEF_LatticeA)
            self.latticeB = get_flt('lattice_parameters_b', self.DEF_LatticeB)
            self.latticeC = get_flt('lattice_parameters_c', self.DEF_LatticeC)
            self.latticeAlpha = get_flt('lattice_parameters_alpha', self.DEF_LatticeAlpha)
            self.latticeBeta = get_flt('lattice_parameters_beta', self.DEF_LatticeBeta)
            self.latticeGamma = get_flt('lattice_parameters_gamma', self.DEF_LatticeGamma)
            self.scatterU1 = get_flt('scattering_Plane_u_1', self.DEF_ScatterU1)
            self.scatterU2 = get_flt('scattering_Plane_u_2', self.DEF_ScatterU2)
            self.scatterU3 = get_flt('scattering_Plane_u_3', self.DEF_ScatterU3)
            self.scatterV1 = get_flt('scattering_Plane_v_1', self.DEF_ScatterV1)
            self.scatterV2 = get_flt('scattering_Plane_v_2', self.DEF_ScatterV2)
            self.scatterV3 = get_flt('scattering_Plane_v_3', self.DEF_ScatterV3)

    def error(self, message):
        raise RuntimeError('DNS reduction error: ' + message)

    def _search_file(self, path, name):
        files = os.listdir(path)
        for file in files:
            if file.__contains__(name):
                return True
        return False

    def _search_fs(self, path, prefix, suffix, run_numbers):
        numbers = run_numbers.split(",")
        fs = []
        found = False
        for run_number in numbers:
            if run_number.__contains__(":"):
                (start, stop) = run_number.split(":")
                start = int(start)
                stop = int(stop)
                for i in range(start, stop+1):
                    for f in os.listdir(path):
                        if re.match(r"{}0*{}{}.d_dat$".format(prefix, int(i), suffix), f):
                            found = True
                            fs.append(str(f))
                    if not found:
                        self.error('file with prefix ' + prefix + ', run number '
                                   + str(i) + ' and suffix ' + suffix + ' not found')
                    found = False
            else:
                for f in os.listdir(path):
                    if re.match(r"{}0*{}{}.d_dat".format(prefix, int(run_number), suffix), f):
                        print('append ',f)
                        found = True
                        fs.append(str(f))
                if not found:
                    self.error('file with prefix ' + prefix + ", run number "
                               + str(run_number) + " and suffix " + suffix + " not found")
                found = False

        return fs

    def to_script(self):

        if not os.path.lexists(self.sampleDataPath):
            self.error('sample data path not found')

        if not self.filePrefix:
            self.error('missing sample data file prefix')

        if not self.fileSuffix:
            self.error('missing sample data file suffix')

        (first_runs, first_workspace, first_comment) = self.dataRuns[0]
        if not self.dataRuns:
            self.error('Missing sample data runs')
        elif not first_runs and not first_workspace and not first_comment:
            self.error("First line empty")

        for (runs, workspace, comment) in self.dataRuns:
            if not runs:
                self.error("All rows must contain run numbers")
            elif runs and not workspace:
                self.error("There must be a workspace to all run numbers")

        for i in range(len(self.maskAngles)):

            (minA, maxA) = self.maskAngles[i]

            if not maxA:
                maxA = 180
            elif not minA:
                minA = 0

            if float(minA) < 0.0 or float(minA) > 180.0:
                errormess = "Angle must be between 0.0 and 180.0 (error in row " + str(i+1) + ' min angle)'
                self.error(errormess)

            if float(maxA) < 0.0 or float(maxA) > 180.0:
                errormess = "Angle must be between 0.0 and 180.0 (error in row " + str(i+1) + ' max angle)'
                self.error(errormess)

            if not float(minA) < float(maxA):
                errormess = 'Min Angle must be smaller than max Angle (error in row ' + str(i+1) + ')'
                self.error(errormess)

        if self.saveToFile:
            if not os.path.lexists(self.outDir):
                self.error('output directory not found')
            elif not os.access(self.outDir, os.W_OK):
                self.error('cant write in directory ' + str(self.outDir))

            if not self.outPrefix:
                self.error('missing output file prefix')

        if not os.path.lexists(self.standardDataPath):
            self.error('standard data path not found')
        else:
            tmp = api.LoadEmptyInstrument(InstrumentName='DNS')
            instrument = tmp.getInstrument()
            api.DeleteWorkspace(tmp)
            if self.detEffi:
                detEffiFilename = instrument.getStringParameter("vana")[0]
                found = self._search_file(self.standardDataPath, detEffiFilename)
                if not found:
                    self.error('no file for detector efficiency correction in '
                               + str(self.standardDataPath) + ' found')
            if self.subInst or self.detEffi or self.flippRatio:
                subInstFilename = instrument.getStringParameter("bkg")[0]
                found = self._search_file(self.standardDataPath, subInstFilename)
                if not found:
                    self.error('no file to subtract of instrument background for sample in '
                               + str(self.standardDataPath) + ' found')
            if self.flippRatio:
                flippRatioFilename = instrument.getStringParameter("nicr")[0]
                found = self._search_file(self.standardDataPath, flippRatioFilename)
                if not found:
                    self.error('no file for flipping ratio correction in '
                               + str(self.standardDataPath) + ' found')

        if self.out == self.OUT_POLY_AMOR and not self.outAxisQ and not self.outAxisD and not self.outAxis2Theta:
            self.error('no abscissa selected')

        parameters = OrderedDict()

        sampleData = OrderedDict()

        sampleData['Data path'] = self.sampleDataPath
        sampleData['File prefix'] = self.filePrefix
        sampleData['File suffix'] = self.fileSuffix
        runs = OrderedDict()
        workspaces = []
        _files = []
        comments = []
        for i in range(len(self.dataRuns)):
            run = OrderedDict()
            (runNumber, outWs, comment) = self.dataRuns[i]
            workspaces.append(str(outWs))
            _files.append(self._search_fs(self.sampleDataPath, self.filePrefix, self.fileSuffix, runNumber))
            comments.append(str(comment))

        sampleData['Data Table workspaces'] = workspaces
        sampleData['Data Table files'] = _files
        sampleData['Data Table comments'] = comments

        parameters['Sample Data'] = sampleData

        minAngles = []
        maxAngles = []
        maskDet = OrderedDict()
        for i in range(len(self.maskAngles)):
            mask = OrderedDict()
            (minA, maxA) = self.maskAngles[i]
            minAngles.append(minA)
            maxAngles.append(maxA)

        maskDet['Min angles'] = minAngles
        maskDet['Max angles'] = maxAngles

        parameters['Mask Detectors'] = maskDet

        saveToFile = OrderedDict()

        saveToFile['Save to file?'] = str(self.saveToFile)
        if self.saveToFile:
            saveToFile['Output directory'] = self.outDir
            saveToFile['Output file prefix'] = self.outPrefix

        parameters['Save'] = saveToFile

        stdData = OrderedDict()

        stdData['Path'] = self.standardDataPath

        parameters['Standard Data'] = stdData

        datRedSettings = OrderedDict()

        datRedSettings['Detector efficiency correction'] = str(self.detEffi)
        datRedSettings['Sum Vandium over detector position'] = str(self.sumVan)
        datRedSettings['Subtract instrument background for sample'] = str(self.subInst)
        if self.subInst:
            datRedSettings['Subtract factor'] = self.subFac
        datRedSettings['Flipping ratio correction'] = str(self.flippRatio)
        if self.flippRatio:
            datRedSettings['Flipping ratio factor'] = self.flippFac
        datRedSettings['Multiple SF scattering probability'] = self.multiSF
        if self.normalise == self.NORM_MONITOR:
            norm = 'monitor'
        else:
            norm = 'time'
        datRedSettings['Normalization'] = norm
        datRedSettings['Neutron wavelength'] = self.neutronWaveLen

        parameters['Data reduction settings'] = datRedSettings

        type = OrderedDict()

        if self.out == self.OUT_POLY_AMOR:
            type['Type'] = 'Polycrystal/Amorphous'
            outAx = []

            if self.outAxisD:
                outAx.append('d-Spacing')

            if self.outAxisQ:
                outAx.append('|Q|')

            if self.outAxis2Theta:
                outAx.append('2theta')

            type['Abscissa'] = str(outAx)
            if self.separation == self.SEP_XYZ:
                type['Separation'] = 'XYZ'
            elif self.separation == self.SEP_COH:
                type['Separation'] = 'Coherent/Incoherent'
            else:
                type['Separation'] = 'No'

        if self.out == self.OUT_SINGLE_CRYST:
            type['Type'] = 'Single Crystal'

            type['Omega offset'] = self.omegaOffset

            lattice = {}
            lattice['a'] = self.latticeA
            lattice['b'] = self.latticeB
            lattice['c'] = self.latticeC
            lattice['alpha'] = self.latticeAlpha
            lattice['beta'] = self.latticeBeta
            lattice['gamma'] = self.latticeGamma

            type['Lattice parameters'] = lattice

            scatter = {}
            u = str(self.scatterU1) + ', ' + str(self.scatterU2) + ', ' + str(self.scatterU3)
            v = str(self.scatterV1) + ', ' + str(self.scatterV2) + ', ' + str(self.scatterV3)
            scatter['u'] = u
            scatter['v'] = v

            type['Scattering Plane'] = scatter

        parameters['Sample'] = type

        script = ['']

        def l(line=''):
            script[0] += line + '\n'

        l("import numpy as np")
        l("import os")
        l()
        l("def is_in_list(angle_list, angle, tolerance):")
        l("    for a in angle_list:")
        l("        if np.fabs(a - angle) < tolerance:")
        l("            return True")
        l("    return False")
        l()
        l("config['default.facility'] = '{}'".format(self.facility_name))
        l("config['default.instrument'] = '{}'".format(self.instrument_name))
        l()
        l()
        l("datapath = '{}'".format(parameters['Sample Data']['Data path']))
        l("prefix = '{}'".format(parameters['Sample Data']['File prefix']))
        l("suffix = '{}'".format(parameters['Sample Data']['File suffix']))
        l("files = {}".format(_files))
        print(_files)
        l("workspaces = {}".format(workspaces))
        l("comments = {}".format(comments))
        if self.out == self.OUT_POLY_AMOR:
            l("xax = {}".format(parameters['Sample']['Abscissa']))
        else:
            l("xax = ['|Q|']")
        l("flipper_bool = {}".format(parameters['Data reduction settings']['Flipping ratio correction']))
        l()
        l("parametersSample = {}".format(dict(parameters['Sample'])))
        l()
        l("wavelength = '{}'".format(parameters['Data reduction settings']['Neutron wavelength']))
        l("if float(wavelength):")
        l("    dataX = np.zeros(2)")
        l("    dataX.fill(float(wavelength) + 0.00001)")
        l("    dataX[::2] -= 0.000002")
        l("else:")
        l("    dataX = []")
        l("dataX = [str(x) for x in dataX]")
        l("dataX_str = ', '.join(dataX)")
        l("maskAngles = {}".format(self.maskAngles))
        l("maskAngles = [str(angle) for angle in maskAngles]")
        l("maskAnglesStr = '; '.join(maskAngles)")
        if self.out == self.OUT_SINGLE_CRYST:
            l("singleCrystal = 'True'")
        else:
            l("singleCrystal = 'False'")
        if self.flippRatio:
            l("flippFac = '{}'".format(parameters['Data reduction settings']['Flipping ratio factor']))
        l("detEffi = {}".format(self.detEffi))
        l("flippRatio = {}".format(self.flippRatio))
        l("subInst = {}".format(self.subInst))
        if self.subInst:
            l("subInstFac = '{}'".format(parameters['Data reduction settings']['Subtract factor']))
        else:
            l("subInstFac = ''")
        l("norm = '{}'".format(parameters['Data reduction settings']['Normalization']))
        l("stdpath = '{}'".format(parameters['Standard Data']['Path']))
        l("saveToFile = {}".format(parameters['Save']['Save to file?']))
        if self.saveToFile:
            l("filePrefix = '{}'".format(parameters['Save']['Output file prefix']))
            l("fileDirectory = '{}'".format(parameters['Save']['Output directory']))
        l()
        l("for files_run in range(len(files)):")
        l("    files_run_str = ', '.join(files[files_run])")
        l("    print(files_run_str)")
        l("    xax_str = ', '.join(xax)")
        l("    DNSLoadData(FilesList=files_run_str, DataPath=datapath, OutputWorkspace=workspaces[files_run],"
          "                OutputTable='SampleDataTable', XAxisUnit=xax_str, Normalization=norm,"
          "                Wavelength=wavelength, DataX = dataX_str, MaskAngles=maskAnglesStr,"
          "                SampleParameters=str(parametersSample), SingleCrystal=singleCrystal)")
        l("    sample_table = mtd[workspaces[files_run]+'_SampleDataTable']")
        l("    if detEffi:")
        l("        DNSLoadData(StandardType='vana', RefWorkspaces=sample_table, DataPath=stdpath, "
          "                    OutputWorkspace=workspaces[files_run], OutputTable='VanaDataTable',"
          "                    XAxisUnit=xax_str, Normalization=norm, Wavelength=wavelength, DataX=dataX_str,"
          "                    MaskAngles=maskAnglesStr)")
        l("    if flippRatio:")
        l("        DNSLoadData(StandardType='nicr', RefWorkspaces=sample_table, DataPath=stdpath, "
          "                    OutputWorkspace=workspaces[files_run], OutputTable='NicrDataTable',"
          "                    XAxisUnit=xax_str, Normalization=norm, Wavelength=wavelength, DataX=dataX_str, "
          "                    MaskAngles=maskAnglesStr)")
        l("    if detEffi or flippRatio or subInst:")
        l("        DNSLoadData(StandardType='leer', RefWorkspaces=sample_table, DataPath=stdpath,"
          "                    OutputWorkspace=workspaces[files_run], OutputTable='BackgroundDataTable', "
          "                    XAxisUnit=xax_str, Normalization=norm, Wavelength=wavelength, DataX=dataX_str,"
          "                    MaskAngles=maskAnglesStr)")
        l("        DNSProcessStandardData(SampleTable=workspaces[files_run]+'_SampleDataTable', "
          "                               NiCrTable=workspaces[files_run]+'_NicrDataTable', "
          "                               BackgroundTable=workspaces[files_run]+'_BackgroundDataTable', "
          "                               OutputTable='ProcessedDataTable', OutputWorkspace=workspaces[files_run])")
        l("        sample_table = mtd[workspaces[files_run]+'_ProcessedDataTable']")
        l("    if detEffi:")
        l("        DNSProcessVanadium(VanadiumTable=workspaces[files_run]+'_VanaDataTable',"
          "                           BackgroundTable=workspaces[files_run]+'_BackgroundDataTable',"
          "                           SampleTable=workspaces[files_run]+'_ProcessedDataTable', "
          "                           OutputWorkspace = workspaces[files_run], OutputXAxis=xax_str)")
        l("        sample_table = mtd[workspaces[files_run]+'_SampleTableVanaCoef']")
        l("    if flippRatio:")
        l("        DNSProcessNiCr(NiCrTable=workspaces[files_run]+'_NicrDataTable', SampleTable=sample_table,"
          "                       OutputWorkspace=workspaces[files_run], XAxisUnits=xax_str, "
          "                       DetEffiCorrection=str(detEffi), FlippCorrFactor=str(flippFac))")
        l("        sample_table = mtd[workspaces[files_run]+'_SampleTableNiCrCoef']")
        """l("    if saveToFile:")
        l("        DNSProcessSampleData(SampleTable=sample_table, SubtractBackground=str(subInst),"
          "                             SubtractBackgroundFactor=subInstFac, DeteEffiCorrection=str(detEffi),"
          "                             FlippRatioCorrection=str(flippRatio), OutputFileDirectory=fileDirectory,"
          "                             OutputFilePrefix=filePrefix, OutputWorkspace=workspaces[files_run],"
          "                             OutputXAxis=xax_str, SampleParameters=str(parametersSample),"
          "                             Comment=comments[files_run])")
        l("    else:")
        l("        DNSProcessSampleData(SampleTable=sample_table, SubtractBackground=str(subInst),"
          "                             SubtractBackgroundFactor=subInstFac, DeteEffiCorrection=str(detEffi),"
          "                             FlippRatioCorrection=str(flippRatio), OutputWorkspace=workspaces[files_run],"
          "                             OutputXAxis=xax_str, SampleParameters=str(parametersSample),"
          "                             Comment=comments[files_run])")
"""
        return script[0]


class DNSReductionScripter(BaseReductionScripter):

    def __init__(self, name, facility):
        BaseReductionScripter.__init__(self, name, facility)
