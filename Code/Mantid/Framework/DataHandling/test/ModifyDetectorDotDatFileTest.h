#ifndef MANTID_DATAHANDLING_MODIFYDETECTORDOTDAYFILETEST_H_
#define MANTID_DATAHANDLING_MODIFYDETECTORDOTDAYFILETEST_H_

#include <cxxtest/TestSuite.h>
#include "MantidKernel/Timer.h"
#include "MantidKernel/System.h"
#include <iostream>
#include <iomanip>

#include "MantidDataHandling/ModifyDetectorDotDatFile.h"
#include "MantidDataHandling/LoadEmptyInstrument.h"
#include <Poco/File.h>

using namespace Mantid;
using namespace Mantid::DataHandling;
using namespace Mantid::API;


class ModifyDetectorDotDatFileTest : public CxxTest::TestSuite
{
public:
  // This pair of boilerplate methods prevent the suite being created statically
  // This means the constructor isn't called when running other tests
  static ModifyDetectorDotDatFileTest *createSuite() { return new ModifyDetectorDotDatFileTest(); }
  static void destroySuite( ModifyDetectorDotDatFileTest *suite ) { delete suite; }

  
  // Helper to set up a simple workspace for testing
  void makeTestWorkspace(const std::string & ads_name)
  {
    IAlgorithm* loader;
    loader = new Mantid::DataHandling::LoadEmptyInstrument;
    loader->initialize();
    TS_ASSERT_THROWS_NOTHING(loader->setPropertyValue("Filename", "IDFs_for_UNIT_TESTING/MAPS_Definition_Reduced.xml"));
    loader->setPropertyValue("OutputWorkspace", ads_name);
    TS_ASSERT_THROWS_NOTHING( loader->execute() );
    TS_ASSERT( loader->isExecuted() );
    delete loader;
  }


  void test_Init()
  {
    ModifyDetectorDotDatFile alg;
    TS_ASSERT_THROWS_NOTHING( alg.initialize() )
    TS_ASSERT( alg.isInitialized() )
  }
  
  void test_exec()
  {
    ModifyDetectorDotDatFile alg;
    TS_ASSERT_THROWS_NOTHING( alg.initialize() )
    TS_ASSERT( alg.isInitialized() )

    // Create input workspace
    std::string wsName = "ModifyDetectorDotDatFileTestWorkspace";
    makeTestWorkspace(wsName);

    // Test Properties
    TS_ASSERT_THROWS_NOTHING( alg.setPropertyValue("InputWorkspace",wsName) );
    TS_ASSERT_THROWS_NOTHING( alg.setPropertyValue("InputFilename", "detector_few_maps.dat") );
    TS_ASSERT_THROWS_NOTHING( alg.setPropertyValue("OutputFilename", "detector_few_maps_result.dat") );

    // Test execution
    TS_ASSERT_THROWS_NOTHING( alg.execute(); );
    TS_ASSERT( alg.isExecuted() );

    // Check output file
    std::string fullFilename = alg.getPropertyValue("OutputFilename"); //Get absolute path
    // has the algorithm written the output file to disk?
    bool OutputFileExists = Poco::File(fullFilename).exists();
    TS_ASSERT( OutputFileExists );
    // If output file exists do some tests on its contents
    if( OutputFileExists) {
      std::ifstream in(fullFilename.c_str());
      std::string header;
      std::string ignore;
      std::string columnNames;

      // Check header has name of algorithm in it
      getline( in, header);
      bool headerHasNameOfAlgorithmInIt = header.find("ModifyDetectorDotDatFile") != std::string::npos;
      TS_ASSERT( headerHasNameOfAlgorithmInIt );

      // Ignore 2nd line
      TS_ASSERT_THROWS_NOTHING(getline (in, ignore));

      // Now at 3rd line
      TS_ASSERT_THROWS_NOTHING(getline (in, columnNames));
      TS_ASSERT_EQUALS( columnNames.substr(0,9), "  det no.");

      in.close();

    }

    // Remove output file
    Poco::File(fullFilename).remove();
  }
  

};


#endif /* MANTID_DATAHANDLING_MODIFYDETECTORDOTDAYFILETEST_H_ */
