"""
    Sample data options for EQSANS reduction
"""
import xml.dom.minidom
from reduction_gui.reduction.scripter import BaseScriptElement
from reduction_gui.reduction.sans.hfir_background_script import Background as BaseBackground
from reduction_gui.reduction.sans.eqsans_sample_script import SampleData

class Background(BaseBackground):

    class DirectBeam(SampleData.DirectBeam):
        def __init__(self, state=None):
            SampleData.DirectBeam.__init__(self)
            if state is not None:
                self.sample_file = state.sample_file
                self.direct_beam = state.direct_beam
                self.beam_radius = state.beam_radius

        def to_script(self):
            """
                Generate reduction script
            """
            if len(str(self.sample_file).strip())==0 or len(str(self.direct_beam).strip())==0:
                raise RuntimeError, "Direct beam method for background transmission was selected but was selected but all the appropriate data files were not entered."    
            
            return "BckDirectBeamTransmission(\"%s\", \"%s\", beam_radius=%g)\n" % \
            (self.sample_file, self.direct_beam, self.beam_radius)

    class BeamHole(SampleData.BeamHole):        
        def __init__(self, state=None):
            SampleData.BeamHole.__init__(self)

        def to_script(self):
            """
                Generate reduction script
            """
            return "BckBeamStopTransmission()\n"
            
    trans_calculation_method = DirectBeam()
    # Option list
    option_list = [DirectBeam]
    # Option to fit the two frame separately when in frame-skipping mode
    combine_transmission_frames = True

    def reset(self):
        """
            Reset state
        """
        super(Background, self).reset()
        self.trans_calculation_method = Background.trans_calculation_method
        self.combine_transmission_frames = SampleData.combine_transmission_frames
    
    def __init__(self):
        super(Background, self).__init__()
        self.reset()

    def to_script(self):
        """
            Generate reduction script
            @param execute: if true, the script will be executed
        """
        script = super(Background, self).to_script()
        if self.background_corr and self.bck_transmission_enabled and self.calculate_transmission:
            script += "BckCombineTransmissionFits(%s)\n" % self.combine_transmission_frames
        return script
            
    def to_xml(self):
        """
            Create XML from the current data.
        """
        xml_str = super(Background, self).to_xml()
        return BaseScriptElement.addElementToSection(xml_str, "Background", "combine_transmission_frames", 
                                                     str(self.combine_transmission_frames))
    
    def from_xml(self, xml_str):
        """
            Read in data from XML
            @param xml_str: text to read the data from
        """    
        self.reset()   
        super(Background, self).from_xml(xml_str)
        
        dom = xml.dom.minidom.parseString(xml_str)
        element_list = dom.getElementsByTagName("Background")
        if len(element_list)>0:
            instrument_dom = element_list[0]      
            self.combine_transmission_frames = BaseScriptElement.getBoolElement(dom, "combine_transmission_frames",
                                                                                default = SampleData.combine_transmission_frames)


    