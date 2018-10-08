#ifndef MANTID_MDALGORITHMS_LOADDNSSCDEWTEST_H_
#define MANTID_MDALGORITHMS_LOADDNSSCDEWTEST_H_

#include "MantidKernel/Strings.h"
#include "MantidAPI/AnalysisDataService.h"
//#include "MantidAPI/IMDIterator.h"
//#include "MantidAPI/IMDEventWorkspace.h"
//#include "MantidDataObjects/MDBox.h"
//#include "MantidDataObjects/MDGridBox.h"
//#include "MantidDataObjects/EventFactory.h"
#include "MantidDataObjects/EventWorkspace.h"
#include "MantidAPI/ExperimentInfo.h"
#include "MantidAPI/Run.h"
#include "MantidKernel/TimeSeriesProperty.h"
#include "MantidAPI/ITableWorkspace.h"
#include "MantidAPI/WorkspaceFactory.h"
#include "MantidAPI/AlgorithmFactory.h"
#include "MantidDataHandling/LoadDNSEvent.h"
#include <boost/range/irange.hpp>
#include <cxxtest/TestSuite.h>

using namespace Mantid;
using namespace Mantid::Kernel;
using namespace Mantid::API;
using namespace Mantid::DataObjects;
using namespace Mantid::DataHandling;

class LoadDNSEventTest : public CxxTest::TestSuite {
public:
  // This pair of boilerplate methods prevent the suite being created statically
  // This means the constructor isn't called when running other tests
  static LoadDNSEventTest *createSuite() { return new LoadDNSEventTest(); }
  static void destroySuite(LoadDNSEventTest *suite) { delete suite; }

  LoadDNSEventTest() {}

  std::shared_ptr<LoadDNSEvent> makeAlgorithm(bool doesThrow = true) {
    std::shared_ptr<LoadDNSEvent> alg(new LoadDNSEvent());
    alg->setRethrows(doesThrow);
    alg->initialize();
    TS_ASSERT(alg->isInitialized());
    return alg;
  }

  std::shared_ptr<LoadDNSEvent> makeAlgorithm(const std::string &inputFile, const std::string &outputWorkspace, bool doesThrow = true) {
    auto alg = makeAlgorithm(doesThrow);
    TS_ASSERT_THROWS_NOTHING(alg->setPropertyValue("InputFile", inputFile));
    TS_ASSERT_THROWS_NOTHING(alg->setPropertyValue("OutputWorkspace", outputWorkspace));
    return alg;
  }

  std::shared_ptr<LoadDNSEvent> makeAlgorithm(const std::string &inputFile, uint chopperChannel, uint monitorChannel, const std::string &outputWorkspace, bool doesThrow = true) {
    auto alg = makeAlgorithm(inputFile, outputWorkspace, doesThrow);
    TS_ASSERT_THROWS_NOTHING(alg->setProperty("chopperChannel", chopperChannel));
    TS_ASSERT_THROWS_NOTHING(alg->setProperty("monitorChannel", monitorChannel));
    return alg;
  }

  void test_Init() {
    LoadDNSEvent alg;
    alg.setRethrows(true);
    TS_ASSERT_THROWS_NOTHING(alg.initialize());
    TS_ASSERT(alg.isInitialized());
  }

  void test_Name() {
    LoadDNSEvent alg;
    TS_ASSERT_EQUALS(alg.name(), "LoadDNSEvent");
  }


  void test_Properties() {
    auto alg = makeAlgorithm();
    TS_ASSERT_EQUALS(alg->getPropertyValue("chopperChannel"), "1");
    TS_ASSERT_EQUALS(alg->getPropertyValue("monitorChannel"), "1");

    TS_ASSERT_THROWS(alg->setProperty("chopperChannel", 5), std::invalid_argument);
    TS_ASSERT_THROWS(alg->setProperty("monitorChannel", 5), std::invalid_argument);
    // TODO: test case when chopper/monitor-Channel set to 0; should get value from definition file

  }

  void test_Executes_1() {
    std::string outWSName("LoadDNSEventTest_OutputWS");

    auto alg = makeAlgorithm(m_fileName, 0, 0, outWSName);
    TS_ASSERT_THROWS_NOTHING(alg->execute(););
    TS_ASSERT(alg->isExecuted());
  }

  void test_Executes_2() {
    std::string outWSName("LoadDNSEventTest_OutputWS");

    auto alg = makeAlgorithm(m_fileName, 1, 4, outWSName);
    TS_ASSERT_THROWS_NOTHING(alg->execute(););
    TS_ASSERT(alg->isExecuted());
  }

  void test_ThrowsOnBadFile() {
    std::string outWSName("LoadDNSEventTest_OutputWS");

    auto alg = makeAlgorithm(m_badFileName, 1, 4, outWSName);
    TS_ASSERT_THROWS(alg->execute(), std::runtime_error);
    TS_ASSERT(!alg->isExecuted());
  }

  void test_DataWSStructure() {
    std::string outWSName("LoadDNSEventTest_OutputWS");
    std::string normWSName("LoadDNSEventTest_OutputWS_norm");

    auto alg = makeAlgorithm(m_fileName, 0, 0, outWSName);
    alg->execute();

    // Retrieve the workspace from data service.
    EventWorkspace_sptr iws;
    TS_ASSERT_THROWS_NOTHING(
        iws = AnalysisDataService::Instance().retrieveWS<EventWorkspace>(
            outWSName));
    TS_ASSERT(iws);

    TS_ASSERT_EQUALS(iws->getEventType(), EventType::TOF);
    TS_ASSERT_EQUALS(iws->size(), 960*128+24); // number of detector cells


    TS_ASSERT_EQUALS(iws->getNumDims(), 2);
    TS_ASSERT_EQUALS(iws->id(), "EventWorkspace");

    // test dimensions
    const auto tofDim = iws->getDimension(0);
    TS_ASSERT(tofDim);
    TS_ASSERT_EQUALS(tofDim->getName(), "Time-of-flight");
    TS_ASSERT_EQUALS(tofDim->getNBins(), 1);

    const auto specDim = iws->getDimension(1);
    TS_ASSERT(specDim);
    TS_ASSERT_EQUALS(specDim->getName(), "Spectrum");
    TS_ASSERT_EQUALS(specDim->getNBins(), 960*128+24); // number of detector cells
    TS_ASSERT_RELATION(std::greater<double>, specDim->getMinimum(), 0);
    TS_ASSERT_RELATION(std::greater<double>, specDim->getMaximum(), 0);

    const auto rng = boost::irange(0ul, iws->size());
    const size_t eventCount = std::accumulate(rng.begin(), rng.end(), 0ul, [&](auto a, auto b) {
      return a + iws->getSpectrum(b).getEvents().size();
    });
    TS_ASSERT_EQUALS(eventCount, 6721)

    AnalysisDataService::Instance().remove(outWSName);
  }

private:
  const std::string m_fileName = "/home/jochimcoenen/Programming/testdata/DNS/data/00550232.mdat";

  const std::string m_badFileName = "dn134011vana.d_dat";
};//"/home/jochimcoenen/MantidExternalData/MD5/28151e3198f9f57b18b97d87627eadf6",#
#endif /* MANTID_MDALGORITHMS_LOADDNSSCDEWEST_H_ */
