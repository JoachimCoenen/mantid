# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
#     NScD Oak Ridge National Laboratory, European Spallation Source
#     & Institut Laue - Langevin
# SPDX - License - Identifier: GPL - 3.0 +
from __future__ import (absolute_import, division, print_function)

import unittest
from mantid.api import MatrixWorkspace
from mantid.simpleapi import SANSILLReduction, config, mtd


class SANSILLReductionTest(unittest.TestCase):

    _facility = None

    def setUp(self):
        self._facility = config['default.facility']
        config.appendDataSearchSubDir('ILL/D11/')
        config['default.facility'] = 'ILL'

    def tearDown(self):
        config['default.facility'] = self._facility
        mtd.clear()

    def test_absorber(self):
        SANSILLReduction(Run='010462', ProcessAs='Absorber', OutputWorkspace='Cd')
        self._check_output(mtd['Cd'])
        self._check_process_flag(mtd['Cd'], 'Absorber')

    def test_beam(self):
        SANSILLReduction(Run='010414', ProcessAs='Beam', OutputWorkspace='Db')
        self._check_output(mtd['Db'])
        self._check_process_flag(mtd['Db'], 'Beam')
        run = mtd['Db'].getRun()
        self.assertAlmostEqual(run.getLogData('BeamCenterX').value, -0.0048, delta=1e-4)
        self.assertAlmostEqual(run.getLogData('BeamCenterY').value, -0.0027, delta=1e-4)
        self.assertAlmostEqual(run.getLogData('BeamFluxValue').value, 6618939, delta=1)
        self.assertAlmostEqual(run.getLogData('BeamFluxError').value, 8554, delta=1)

    def test_transmission(self):
        SANSILLReduction(Run='010414', ProcessAs='Beam', OutputWorkspace='Db')
        SANSILLReduction(Run='010585', ProcessAs='Transmission', BeamInputWorkspace='Db', OutputWorkspace='Tr')
        self.assertAlmostEqual(mtd['Tr'].readY(0)[0], 0.640, delta=1e-3)
        self.assertAlmostEqual(mtd['Tr'].readE(0)[0], 0.0019, delta=1e-4)
        self._check_process_flag(mtd['Tr'], 'Transmission')

    def test_container(self):
        SANSILLReduction(Run='010460', ProcessAs='Container', OutputWorkspace='can')
        self._check_output(mtd['can'])
        self._check_process_flag(mtd['can'], 'Container')

    def test_reference(self):
        SANSILLReduction(Run='010453', ProcessAs='Reference', SensitivityOutputWorkspace='sens', OutputWorkspace='water')
        self._check_output(mtd['water'])
        self._check_output(mtd['sens'], logs=False)
        self._check_process_flag(mtd['water'], 'Reference')
        self._check_process_flag(mtd['sens'], 'Sensitivity')

    def test_sample(self):
        SANSILLReduction(Run='010569', ProcessAs='Sample', OutputWorkspace='sample')
        self._check_output(mtd['sample'])
        self._check_process_flag(mtd['sample'], 'Sample')

    def _check_process_flag(self, ws, value):
        self.assertTrue(ws.getRun().getLogData('ProcessedAs').value, value)

    def _check_output(self, ws, logs=True):
        self.assertTrue(ws)
        self.assertTrue(isinstance(ws, MatrixWorkspace))
        self.assertTrue(ws.isHistogramData())
        self.assertEqual(ws.getAxis(0).getUnit().unitID(), "Wavelength")
        self.assertEqual(ws.blocksize(), 1)
        self.assertEqual(ws.getNumberHistograms(), 128 * 128)
        self.assertTrue(ws.getInstrument())
        self.assertTrue(ws.getRun())
        self.assertTrue(ws.getSampleDetails())
        self.assertTrue(ws.getHistory())
        if logs:
            self.assertTrue(ws.getRun().hasProperty('qmin'))
            self.assertTrue(ws.getRun().hasProperty('qmax'))
            self.assertTrue(ws.getRun().hasProperty('l2'))
            self.assertTrue(ws.getRun().hasProperty('pixel_height'))
            self.assertTrue(ws.getRun().hasProperty('pixel_width'))
            self.assertTrue(ws.getRun().hasProperty('collimation.actual_position'))

if __name__ == '__main__':
    unittest.main()
