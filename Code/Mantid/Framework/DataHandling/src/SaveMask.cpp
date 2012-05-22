/*WIKI*



This algorithm saves a SpecialWorkspace2D/MaskWorkspace to an XML file.


*WIKI*/

#include "MantidDataHandling/SaveMask.h"
#include "MantidKernel/System.h"
#include "MantidAPI/FileProperty.h"
#include "MantidAPI/ISpectrum.h"
#include "MantidGeometry/IDetector.h"

#include "fstream"
#include "sstream"
#include "algorithm"

#include "Poco/DOM/Document.h"
#include "Poco/DOM/Element.h"
#include "Poco/DOM/Text.h"
#include "Poco/DOM/AutoPtr.h"
#include "Poco/DOM/DOMWriter.h"
#include "Poco/XML/XMLWriter.h"

using namespace Mantid::Kernel;
using namespace Mantid::API;

using namespace Poco::XML;

namespace Mantid
{
namespace DataHandling
{

  DECLARE_ALGORITHM(SaveMask)

  //----------------------------------------------------------------------------------------------
  /**
   * Constructor
   */
  SaveMask::SaveMask()
  {
  }

  //----------------------------------------------------------------------------------------------
  /** Destructor
   */
  SaveMask::~SaveMask()
  {
  }
  
  /// Sets documentation strings for this algorithm
  void SaveMask::initDocs()
  {
    this->setWikiSummary("Save a mask workspace to an XML file.");
    this->setOptionalMessage("Mask workspace can be a MaskWorkspace or a regular MatrixWorkspace. "
        "In the second case, the detectors' masking information come from detectors. ");
  }

  /// Define input parameters
  void SaveMask::init()
  {
    declareProperty(new API::WorkspaceProperty<API::MatrixWorkspace>("InputWorkspace", "", Direction::Input),
        "MaskingWorkspace (MaskWorkspace or regular MatrixWorkspace) to output to XML file (SpecialWorkspace2D)");
    declareProperty(new FileProperty("OutputFile", "", FileProperty::Save, ".xml"),
        "File to save the detectors mask in XML format");
    declareProperty("GroupedDetectors", false,
        "True if there can be more than one detector contained in any spectrum. ");

  }

  /// Main body to execute algorithm
  void SaveMask::exec()
  {
    // 1. Get input
    API::MatrixWorkspace_const_sptr inpWS = this->getProperty("InputWorkspace");
    // DataObjects::SpecialWorkspace2D_const_sptr inpWS = this->getProperty("InputWorkspace");
    std::string outxmlfilename = this->getPropertyValue("OutputFile");

    // 2. Convert Workspace to a list of detectors of masked
    std::vector<detid_t> detid0s;

    bool ismaskworkspace;
    DataObjects::MaskWorkspace_const_sptr inpMaskWS = boost::dynamic_pointer_cast<const DataObjects::MaskWorkspace>(inpWS);
    if (inpMaskWS)
    {
      ismaskworkspace = true;
    }
    else
    {
      ismaskworkspace = false;
    }

    if (ismaskworkspace)
    {
      getMaskedDetectorsFromMaskWorkspace(inpMaskWS, detid0s);
    }
    else
    {
      getMaskedDetectorsFromInstrument(inpWS, detid0s);
    }


    // d) sort
    g_log.debug() << "Number of detectors to be masked = " << detid0s.size() << std::endl;

    // 3. Count workspace to count 1 and 0
    std::vector<detid_t> idx0sts;  // starting point of the pair
    std::vector<detid_t> idx0eds;  // ending point of pair

    if (!detid0s.empty())
    {
      std::sort(detid0s.begin(), detid0s.end());

      detid_t i0st = detid0s[0];
      detid_t i0ed = detid0s[0];

      for (size_t i = 1; i < detid0s.size(); i ++){

        if (detid0s[i] == detid0s[i-1]+1){
          // If it is continuous: record the current one
          i0ed = detid0s[i];
        } else {
          // If skip: restart everything
          // i) record previous result
          idx0sts.push_back(i0st);
          idx0eds.push_back(i0ed);
          // ii) reset the register
          i0st = detid0s[i];
          i0ed = detid0s[i];
        }

      } // for

      // Complete the registration
      idx0sts.push_back(i0st);
      idx0eds.push_back(i0ed);

      for (size_t i = 0; i < idx0sts.size(); i++){
        g_log.information() << "Section " << i << " : " << idx0sts[i] << "  ,  " << idx0eds[i] << " to be masked and recorded."<< std::endl;
      }
    } // Only work for detid > 0

    // 4. Write out to XML nodes
    // a) Create document and root node
    AutoPtr<Document> pDoc = new Document;
    AutoPtr<Element> pRoot = pDoc->createElement("detector-masking");
    pDoc->appendChild(pRoot);
    // pRoot->setAttribute("default", "use");

    // b) Append Group
    AutoPtr<Element> pChildGroup = pDoc->createElement("group");
    // pChildGroup->setAttribute("type", "notuse");
    pRoot->appendChild(pChildGroup);

    // c) Append detid
    // c1. Generate text value
    std::stringstream ss;
    for (size_t i = 0; i < idx0sts.size(); i ++)
    {
      size_t ist = idx0sts[i];
      size_t ied = idx0eds[i];

      // a-b or a
      bool writedata = true;
      if (ist < ied){
        ss << ist << "-" << ied;
      } else if (ist == ied){
        ss << ist;
      } else {
        writedata = false;
      }
      // add ","
      if (writedata && i < idx0sts.size()-1){
        ss << ",";
      }

    } // for
    std::string textvalue = ss.str();
    g_log.debug() << "SaveMask main text:  available section = " << idx0sts.size() << "\n" << textvalue << std::endl;

    // c2. Create element
    AutoPtr<Element> pDetid = pDoc->createElement("detids");
    AutoPtr<Text> pText1 = pDoc->createTextNode(textvalue);
    pDetid->appendChild(pText1);
    pChildGroup->appendChild(pDetid);

    // 4. Write
    DOMWriter writer;
    writer.setNewLine("\n");
    writer.setOptions(XMLWriter::PRETTY_PRINT);

    std::ofstream ofs;
    ofs.open(outxmlfilename.c_str(), std::fstream::out);

    ofs << "<?xml version=\"1.0\"?>\n";

    writer.writeNode(std::cout, pDoc);
    writer.writeNode(ofs, pDoc);
    ofs.close();

    return;
  }

  /*
   * Get the list of detector IDs for detectors that are masked
   */
  void SaveMask::getMaskedDetectorsFromMaskWorkspace(DataObjects::MaskWorkspace_const_sptr inpWS, std::vector<detid_t>& detidlist)
  {
    for (size_t i = 0; i < inpWS->getNumberHistograms(); i ++)
    {
      if (inpWS->dataY(i)[0] > 0.1)
      {
        // It is way from 0 but smaller than 1
        // a) workspace index -> spectrum -> detector ID
        const API::ISpectrum *spec = inpWS->getSpectrum(i);
        if (!spec)
        {
          g_log.error() << "No spectrum corresponds to workspace index " << i << std::endl;
          throw std::invalid_argument("Cannot find spectrum");
        }

        const std::set<detid_t> detids = spec->getDetectorIDs();
        if (detids.size() != 1)
        {
          g_log.error() << "Impossible Situation! Workspace " << i << " corresponds to #(Det) = " << detids.size() << std::endl;
          throw std::invalid_argument("Impossible number of detectors");
        }

        // b) get detector id & Store
        detid_t detid;;
        std::set<detid_t>::const_iterator it;
        for (it=detids.begin(); it!=detids.end(); ++it)
        {
          detid = *it;
        }

        // c) store
        detidlist.push_back(detid);
      } // if
    } // for

    return;
  }

  /*
   * Get the list of masked detectors' IDs
   */
  void SaveMask::getMaskedDetectorsFromInstrument(API::MatrixWorkspace_const_sptr inpWS, std::vector<detid_t>& detidlist)
  {
    // 1. Get instrument
    Geometry::Instrument_const_sptr instrument = inpWS->getInstrument();
    if (!instrument)
    {
      g_log.error() << "InputWorkspace " << inpWS->getName() << " has no instrument (NULL). " << std::endl;
      throw std::invalid_argument("InputWorkspace has no instrument. ");
    }

    for (size_t iw = 0; iw < inpWS->getNumberHistograms(); ++iw)
    {
      const API::ISpectrum *spec = inpWS->getSpectrum(iw);
      std::set<int> detids = spec->getDetectorIDs();
      bool ismasked = inpWS->getDetector(iw)->isMasked();
      if (ismasked)
      {
        for (std::set<int>::iterator dit = detids.begin(); dit != detids.end(); ++dit)
        {
          detid_t detid = detid_t(*dit);
          detidlist.push_back(detid);
        }
      }
    }

    return;
  }


} // namespace DataHandling
} // namespace Mantid
