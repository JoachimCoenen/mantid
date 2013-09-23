#ifndef MANTID_MDEVENTS_MDBOX_FLATTREE_H_
#define MANTID_MDEVENTS_MDBOX_FLATTREE_H_

#include "MantidAPI/FrameworkManager.h"
#include "MantidMDEvents/MDBoxFlatTree.h"
#include "MantidTestHelpers/MDEventsTestHelper.h"
#include "MantidMDEvents/MDLeanEvent.h"
#include "MantidAPI/BoxController.h"

#include <cxxtest/TestSuite.h>
#include <Poco/File.h>

using namespace Mantid;
using namespace Mantid::MDEvents;

class MDBoxFlatTreeTest :public CxxTest::TestSuite
{
private:
  
    Mantid::API::IMDEventWorkspace_sptr spEw3;

public:
  // This pair of boilerplate methods prevent the suite being created statically
  // This means the constructor isn't called when running other tests
  static MDBoxFlatTreeTest  *createSuite() { return new MDBoxFlatTreeTest (); }
  static void destroySuite( MDBoxFlatTreeTest  *suite ) { delete suite; }

  void testFlatTreeOperations()
  {
    MDBoxFlatTree BoxTree;

    TS_ASSERT_EQUALS(0,BoxTree.getNBoxes());

    TS_ASSERT_THROWS_NOTHING((BoxTree.initFlatStructure(spEw3,"aFile")));

    TSM_ASSERT_EQUALS("Workspace creatrion helper should generate ws split into 1001 boxes",1001,BoxTree.getNBoxes());

    TS_ASSERT_THROWS_NOTHING(BoxTree.saveBoxStructure("someFile.nxs"));

    Poco::File testFile("someFile.nxs");
    TSM_ASSERT("BoxTree was not able to create test file",testFile.exists());


    MDBoxFlatTree BoxStoredTree;
    TSM_ASSERT_THROWS("Should throw as the box data were written for lean event and now we try to retrieve full events",
      BoxStoredTree.loadBoxStructure("someFile.nxs",3,"MDEvent"),std::runtime_error);

    TS_ASSERT_THROWS_NOTHING(BoxStoredTree.loadBoxStructure("someFile.nxs",3,"MDLeanEvent"));

    size_t nDim = size_t(BoxStoredTree.getNDims());
    API::BoxController_sptr new_bc = boost::shared_ptr<API::BoxController>(new API::BoxController(nDim));    
    new_bc->fromXMLString(BoxStoredTree.getBCXMLdescr());

    TSM_ASSERT("Should restore the box controller equal to the one before saving ",*(spEw3->getBoxController())==*(new_bc));

    std::vector<API::IMDNode *>Boxes;
    TS_ASSERT_THROWS_NOTHING(BoxStoredTree.restoreBoxTree(Boxes ,new_bc, false,false));

    if(testFile.exists())
      testFile.remove();
  }

  MDBoxFlatTreeTest()
  {
      // load dependent DLL, which are used in MDEventsTestHelper (e.g. MDAlgorithms to create MD workspace)
//      Mantid::API::FrameworkManager::Instance();
    // make non-file backet mdEv workspace with 10000 events
     spEw3 = MDEventsTestHelper::makeFileBackedMDEW("TestLeanEvWS", false,10000);
  }

};


#endif