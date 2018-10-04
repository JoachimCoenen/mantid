﻿#include <sstream>

#include "MantidDataHandling/LoadDNSEvent.h"
#include "MantidKernel/BoundedValidator.h"
#include "MantidAPI/FileProperty.h"
#include "MantidAPI/Run.h"
#include "MantidAPI/SpectraAxis.h"
#include "MantidAPI/NumericAxis.h"
#include "MantidDataObjects/EventWorkspace.h"
#include "MantidGeometry/ICompAssembly.h"
#include "MantidGeometry/IDTypes.h"
#include "MantidGeometry/Instrument.h"
#include "MantidGeometry/Instrument/ComponentInfo.h"
#include "MantidAPI/WorkspaceFactory.h"
#include "MantidKernel/ListValidator.h"
#include "MantidKernel/OptionalBool.h"
#include "MantidKernel/Strings.h"
#include "MantidKernel/System.h"

#include <boost/range/combine.hpp>
#include <ios>
#include <fstream>
#include <vector>
#include <map>
#include <stdexcept>
#include <ostream>

#include <chrono>
#include <sstream>
#include <iostream>

#define USE_PARALLELISM true

//#define LOG_INFORMATION(a) g_log.notice() << a;
#define LOG_INFORMATION(a) //g_log.information()##<<##a;

template<typename TimeT = std::chrono::milliseconds>
struct measure
{
    template<typename F, typename ...Args>
    static typename TimeT::rep execution(F&& func, Args&&... args)
    {
        auto start = std::chrono::steady_clock::now();
        std::forward<decltype(func)>(func)(std::forward<Args>(args)...);
        auto duration = std::chrono::duration_cast< TimeT>
                            (std::chrono::steady_clock::now() - start);
        return duration.count();
    }
};

using measureMicroSecs = measure<std::chrono::microseconds>;

#define MEASURE_MICRO_SECS(op) measureMicroSecs::execution([&]() op )

using namespace Mantid::DataObjects;
using namespace Mantid::Kernel;
using namespace Mantid::API;

namespace Mantid {

namespace DataHandling {

DECLARE_ALGORITHM(LoadDNSEvent)

const std::string LoadDNSEvent::INSTRUMENT_NAME = "DNS";
const uint64_t MAX_BUFFER_BYTES_SIZE = 1500; // maximum buffer size in data file

void LoadDNSEvent::init() {
  /// Initialise the properties

  const std::vector<std::string> exts{".mdat"};
  declareProperty(Kernel::make_unique<FileProperty>("InputFile", "",
                                                    FileProperty::Load, exts),
                  "The XML or Map file with full path.");

  declareProperty(Kernel::make_unique<Kernel::PropertyWithValue<uint>>(
                      "ChopperChannel", 1, boost::shared_ptr<BoundedValidator<uint>>(new BoundedValidator<uint>(0, 4)), Kernel::Direction::Input),
                  "The Chopper Channel");

  declareProperty(Kernel::make_unique<Kernel::PropertyWithValue<uint>>(
                      "MonitorChannel", 1, boost::shared_ptr<BoundedValidator<uint>>(new BoundedValidator<uint>(0, 4)), Kernel::Direction::Input),
                  "The Monitor Channel");

  declareProperty(
      make_unique<WorkspaceProperty<DataObjects::EventWorkspace>>(
          "OutputWorkspace", "", Direction::Output),
      "The name of the output workspace.");
}

/// Run the algorithm
void LoadDNSEvent::exec() {
  const size_t DUMMY_SIZE = 42;
  EventWorkspace_sptr outputWS =  boost::dynamic_pointer_cast<EventWorkspace>(
      WorkspaceFactory::Instance().create("EventWorkspace", 960*128+24, DUMMY_SIZE, DUMMY_SIZE));
  outputWS->switchEventType(Mantid::API::EventType::TOF);
  outputWS->getAxis(0)->setUnit("TOF");

  runLoadInstrument(INSTRUMENT_NAME, outputWS);

  chopperChannel = static_cast<uint>(getProperty("ChopperChannel"));
  monitorChannel = static_cast<uint>(getProperty("MonitorChannel"));
  const auto chopperChannels = outputWS->instrumentParameters().getType<uint>("chopper", "channel");
  const auto monitorChannels = outputWS->instrumentParameters().getType<uint>("monitor", "channel");
  chopperChannel = chopperChannel != 0 ? chopperChannel : (chopperChannels.empty() ? 99 : chopperChannels.at(0));
  monitorChannel = monitorChannel != 0 ? monitorChannel : (monitorChannels.empty() ? 99 : monitorChannels.at(0));
  g_log.notice() << "ChopperChannel: " << chopperChannel << std::endl;
  g_log.notice() << "MonitorChannel: " << monitorChannel << std::endl;

  _eventAccumulator.neutronEvents.resize(960*128+24);

  try {
    FileByteStream file(static_cast<std::string>(getProperty("InputFile")), endian::big);
    //file.exceptions(std::ifstream::eofbit);
    std::pair<long, long> elapsedTimeCombineSplitting;
    long elapsedTimeSorting    = 0;
    //long elapsedTimeTotal = measureMicroSecs::execution([&](){
      auto elapsedTimeParsing    = MEASURE_MICRO_SECS({ elapsedTimeCombineSplitting = parse_File(file); });
      auto elapsedTimeProcessing = MEASURE_MICRO_SECS({ elapsedTimeSorting = populate_EventWorkspace(outputWS); });
    //});

    g_log.notice()
        << " ## elapsedTime Parsing\t= " << elapsedTimeParsing
        << "\n  # elapsedTime Splitting\t= " << elapsedTimeCombineSplitting.first
        << "\n  # elapsedTime Combining\t= " << elapsedTimeCombineSplitting.second
        << "\n ## elapsedTime Processing\t= " << elapsedTimeProcessing
        << "\n  # elapsedTime Sorting\t= " << elapsedTimeSorting
        << "\n### elapsedTime Total  \t= " << elapsedTimeParsing + elapsedTimeProcessing
        << std::endl;


  } catch (std::runtime_error e) {
    g_log.error(e.what());
  }
  //        g_log.notice()
  //            << std::setprecision(15) << std::fixed << "T"
  //            << ", " << double(event.timestamp) / 10000.0
  //            << std::endl;

  setProperty("OutputWorkspace", outputWS);
  g_log.notice() << std::endl;
}

template<typename Vector, typename _Compare>
void sortVector(Vector &v, _Compare comp) {
  std::sort(v.begin(), v.end(), comp);
}

long LoadDNSEvent::populate_EventWorkspace(EventWorkspace_sptr eventWS) {
  static const uint EVENTS_PER_PROGRESS = 100;
  // The number of steps depends on the type of input file
  Progress progress(this, 0.0, 1.0, _eventAccumulator.neutronEvents.size()/EVENTS_PER_PROGRESS);

  // Sort reversed (latest event first, most early event last):
  auto elapsedTimeSorting = measureMicroSecs::execution([&](){ sortVector(_eventAccumulator.triggerEvents, [](auto l, auto r){ return l.timestamp > r.timestamp; }); });

  g_log.notice() << _eventAccumulator.neutronEvents.size() << std::endl;

  std::atomic<uint64_t> oversizedChanelIndexCounterA(0);
  std::atomic<uint64_t> oversizedPosCounterA(0);

  PARALLEL_FOR_IF(Kernel::threadSafe(*eventWS)&&USE_PARALLELISM)
  for (uint j = 0; j < _eventAccumulator.neutronEvents.size(); j++)
  {
    //uint64_t chopperTimestamp = 0;
    uint64_t oversizedChanelIndexCounter = 0;
    uint64_t oversizedPosCounter = 0;
    uint64_t triggerCounter = 0;
    uint64_t i = 0;
    const auto wsIndex = j;
    auto &eventList = _eventAccumulator.neutronEvents[j];
    if (eventList.size() != 0) {
      std::sort(eventList.begin(), eventList.end(), [](auto l, auto r){ return l.timestamp < r.timestamp; });
    }

    auto chopperIt = _eventAccumulator.triggerEvents.cbegin();

    auto &spectrum = eventWS->getSpectrum(wsIndex);
    //PARALLEL_START_INTERUPT_REGION

    for (const auto &event : eventList) {
      i++;
      if (i%EVENTS_PER_PROGRESS == 0) {
        progress.report();
        if (this->getCancel()) {
          throw CancelException();
        }
      }


//      if ((event.channel & 0b0000000000010000) != 0) {
//        oversizedChanelIndexCounter++;
//      }
//      if (event.position >= 960) {
//        oversizedPosCounter++;
//      }

      chopperIt = std::lower_bound(chopperIt, _eventAccumulator.triggerEvents.cend(),  event.timestamp, [](auto l, auto r){ return l.timestamp > r; });
      const uint64_t chopperTimestamp = chopperIt != _eventAccumulator.triggerEvents.cend() ? chopperIt->timestamp : 0;

      spectrum.addEventQuickly(Types::Event::TofEvent(double(event.timestamp - chopperTimestamp) / 10.0));

    }

    //PARALLEL_END_INTERUPT_REGION
    oversizedChanelIndexCounterA += oversizedChanelIndexCounter;
    oversizedPosCounterA += oversizedPosCounter;
  }
  //PARALLEL_CHECK_INTERUPT_REGION



  g_log.notice() << "Bad chanel indices: " << oversizedChanelIndexCounterA << std::endl;
  g_log.notice() << "Bad position values: " << oversizedPosCounterA << std::endl;
  g_log.notice() << "Trigger Counter: " << _eventAccumulator.triggerEvents.size() << std::endl;
  return elapsedTimeSorting;
}

void LoadDNSEvent::runLoadInstrument(std::string instrumentName, EventWorkspace_sptr &eventWS) {
  IAlgorithm_sptr loadInst = createChildAlgorithm("LoadInstrument");
  // Now execute the Child Algorithm. Catch and log any error, but don't stop.
  try {
    loadInst->setPropertyValue("InstrumentName", instrumentName);
    g_log.debug() << "InstrumentName" << instrumentName << '\n';
    loadInst->setProperty<MatrixWorkspace_sptr>("Workspace", eventWS);
    loadInst->setProperty("RewriteSpectraMap", Mantid::Kernel::OptionalBool(true));

    loadInst->execute();
  } catch (...) {
    g_log.information("Cannot load the instrument definition.");
  }
}

namespace {
template<typename Iterable>
constexpr std::map<
   std::remove_reference_t<decltype(*std::declval<decltype(std::declval<Iterable>().cbegin())>())>,
  size_t
>
buildSkipTable(const Iterable &iterable) {
  std::map<
     std::remove_reference_t<decltype(*std::declval<decltype(std::declval<Iterable>().cbegin())>())>,
    size_t
  > skipTable;

  size_t i = iterable.size();
  for (auto c : iterable) {
    i--;
    auto &cPos = skipTable[c];
    cPos = cPos == 0 ? iterable.size() : cPos;
    cPos = i == 0 ? cPos : i;
  }
  return skipTable;
}

template<typename Iterable>
const std::vector<uint8_t> buildSkipTable2(const Iterable &iterable) {
  std::vector<uint8_t> skipTable(256, iterable.size());

  size_t i = iterable.size();
  for (auto c : iterable) {
    i--;
    auto &cPos = skipTable[c];
    cPos = i == 0 ? cPos : i;
  }
  return skipTable;
}

}

std::vector<uint8_t> LoadDNSEvent::parse_Header(FileByteStream &file) {
  // using Boyer-Moore String Search:
  LOG_INFORMATION("parse_Header...\n")
  static constexpr std::array<uint8_t, 8> header_sep {0x00, 0x00, 0x55, 0x55, 0xAA, 0xAA, 0xFF, 0xFF};
  static const auto skipTable = buildSkipTable(header_sep);

  // search for header_sep and store actual header:
  std::vector<uint8_t> header;

  std::array<uint8_t, header_sep.size()> current_window;
  file.readRaw(current_window);

  int j = 0;
  while (!file.eof() && (j++ < 1024*8)) {
    if (current_window == header_sep) {
      return header;
    } else {
      auto iter = skipTable.find(*current_window.rbegin());
      size_t skip_length = (iter == skipTable.end()) ? header_sep.size() : iter->second;

      const auto orig_header_size = header.size();
      header.resize(header.size() + skip_length);
      const auto win_data = current_window.data();
      std::copy(win_data, win_data + skip_length, header.data() + orig_header_size);

      const std::array<uint8_t, header_sep.size()> orig_window = current_window;
      file.readRaw(current_window, skip_length);
      std::copy(orig_window.data() + skip_length, orig_window.data() + header_sep.size(), win_data);
    }
  }
  //throw std::runtime_error(std::string("STOP!!!! please. (ugh!)"));
  return header;
}

//#define LOG_NOTICE(a) g_log.notice() << a;
#define LOG_NOTICE(a) //g_log.notice()##<<##a;

std::vector<std::vector<uint8_t>> LoadDNSEvent::split_File(FileByteStream &file, const uint maxChunckCount) {
  LOG_INFORMATION("split_File...\n")
  static constexpr std::array<uint8_t, 8> block_sep = {0x00, 0x00, 0xFF, 0xFF, 0x55, 0x55, 0xAA, 0xAA}; // 0xAAAA5555FFFF0000; //
  static const auto skipTable = buildSkipTable2(block_sep);

  const uint64_t minChunckSize = MAX_BUFFER_BYTES_SIZE;
  const uint64_t chunckSize = std::max(minChunckSize, file.fileSize() / maxChunckCount);

  std::vector<std::vector<uint8_t>> result;

  LOG_NOTICE("result.size() = " << result.size() << std::endl);
  while(!file.eof()) {
    result.push_back(std::vector<uint8_t>());
    auto &data = result.back();
    data.resize(chunckSize);
    LOG_NOTICE("data.size() = " << data.size() << std::endl);
    try {
      file.readRaw(*data.begin(), chunckSize);
    } catch (std::ifstream::failure e) {
      LOG_NOTICE("fail.size() = " << data.size() << std::endl);
      data.resize(file.gcount());
      return result;
    }

    LOG_NOTICE("data.size() = " << data.size() << std::endl);


    // search for a block_separator, and append everything up to it :
    static const auto windowSize = block_sep.size();
    uint8_t *current_window = nullptr;
    std::array<uint8_t, windowSize> *windowAsArray = reinterpret_cast<std::array<uint8_t, windowSize>*>(current_window);

//#undef LOG_NOTICE
//#define LOG_NOTICE(a) g_log.notice() << a;
    LOG_NOTICE("\n\n### new Data ###" << std::endl);
    try {
      data.resize(data.size() + windowSize);
      // accomodate for possible relocation of vector...:
      current_window = &*(data.end() - windowSize);
      windowAsArray = reinterpret_cast<std::array<uint8_t, windowSize>*>(current_window);
      file.readRaw(current_window[0], windowSize);

      while (*windowAsArray != block_sep) { // (!file.eof() ) {
        size_t skip_length = skipTable[current_window[windowSize-1]];


        const auto orig_data_size = data.size();
        data.resize(orig_data_size + skip_length);

        // accomodate for possible relocation of vector...:
        current_window = (&data.back() - windowSize+1);

        windowAsArray = reinterpret_cast<std::array<uint8_t, windowSize>*>(current_window);
        file.readRaw(current_window[windowSize - skip_length], skip_length);
      }
    } catch (std::ifstream::failure e) {
      return result;
    }
  } // while
  return result;
}

std::pair<long, long> LoadDNSEvent::parse_File(FileByteStream &file) {
  // File := Header Body
  std::vector<uint8_t> header = parse_Header(file);

  const int threadCount = USE_PARALLELISM ? PARALLEL_GET_MAX_THREADS : 1;

  // Split File:
  std::vector<std::vector<uint8_t>> filechuncks;
  auto elapsedTimeSplitting = MEASURE_MICRO_SECS({ filechuncks = split_File(file, threadCount);});
  g_log.notice() << "filechuncks count = " << filechuncks.size() << std::endl;


   std::vector<EventAccumulator> eventAccumulators;
  eventAccumulators.resize(filechuncks.size());
  for (auto & evtAcc : eventAccumulators) {
    evtAcc.neutronEvents.resize(960*128+24);
  }

  g_log.notice() << "evtAcc.neutronEvents.size() = " << eventAccumulators[eventAccumulators.size()-1].neutronEvents.size() << std::endl;

  //parse file chuncks:
  const auto end = filechuncks.cend();
  size_t j = 0;
  PARALLEL_FOR_IF(USE_PARALLELISM)
  for (auto iter = filechuncks.cbegin(); iter < end; iter++) {
    g_log.notice() << "filechunck.size() = " << iter->size() << std::endl;
    auto vbs = VectorByteStream(*iter, file.endianess);
    const auto fileChunckIndex = iter - filechuncks.cbegin();
    parse_BlockList(vbs, eventAccumulators[size_t(fileChunckIndex)]);
  }

  g_log.notice() << "j = " << j << std::endl;
  // combine eventAccumulators:
  auto elapsedTimeCombining =
  MEASURE_MICRO_SECS(
  {
    PARALLEL {
      PARALLEL_SECTIONS {
        PARALLEL_SECTION {
          auto origSize = _eventAccumulator.triggerEvents.size();
          _eventAccumulator.triggerEvents.resize(std::accumulate(eventAccumulators.cbegin(), eventAccumulators.cend(), 0, [](const auto s, const auto &v){ return s + v.triggerEvents.size(); }));
          for (const auto & evtAcc : eventAccumulators) {
            std::memcpy(_eventAccumulator.triggerEvents.data() + origSize, evtAcc.triggerEvents.data(), evtAcc.triggerEvents.size());
            origSize += evtAcc.triggerEvents.size();
          }
        }
        PARALLEL_SECTION {
          PRAGMA_OMP(for)
          for (int i = -1; i < _eventAccumulator.neutronEvents.size(); ++i) {
            auto origSize = _eventAccumulator.neutronEvents[i].size();
            _eventAccumulator.neutronEvents[i].resize(std::accumulate(eventAccumulators.cbegin(), eventAccumulators.cend(), 0, [&](const auto s, const auto &v){ return s + v.neutronEvents[i].size(); }));
            for (const auto & evtAcc : eventAccumulators) {
              std::memcpy(_eventAccumulator.neutronEvents[i].data() + origSize, evtAcc.neutronEvents[i].data(), evtAcc.neutronEvents[i].size());
              origSize += evtAcc.neutronEvents[i].size();
            }
          }
        }
      }
    }

  });
  //parse_BlockList(file, _eventAccumulator);
  //parse_EndSignature(file);
  return {elapsedTimeSplitting, elapsedTimeCombining};
}

void LoadDNSEvent::parse_BlockList(VectorByteStream &file, EventAccumulator &eventAccumulator) {
  LOG_INFORMATION("parse_BlockList...\n");
  // BlockList := DataBuffer BlockListTrail
  while (!file.eof() && file.peek() != 0xFF) {
    parse_Block(file, eventAccumulator);
  }
}

void LoadDNSEvent::parse_Block(VectorByteStream &file, EventAccumulator &eventAccumulator) {
  LOG_INFORMATION("parse_Block...\n")
  // Block := DataBufferHeader DataBuffer
  parse_DataBuffer(file, eventAccumulator);
  parse_BlockSeparator(file);
}

void LoadDNSEvent::parse_BlockSeparator(VectorByteStream &file) {
  LOG_INFORMATION("parse_BlockSeparator...\n")
  const separator_t block_sep = (0x0000FFFF5555AAAA); // 0xAAAA5555FFFF0000; //
  auto separator = file.read(separator_t());
  if (separator != block_sep) {
    throw std::runtime_error(std::string("File Integrety LOST. (ugh!) 0x") + n2hexstr(separator)
                             + std::string("expected 0x") + n2hexstr(block_sep));
  }
}

void LoadDNSEvent::parse_DataBuffer(VectorByteStream &file, EventAccumulator &eventAccumulator) {
  LOG_INFORMATION("parse_DataBuffer...\n");
  const auto bufferHeader = parse_DataBufferHeader(file);

  const uint16_t dataLength = uint16_t(bufferHeader.bufferLength - 21);
  const auto event_count = dataLength / 3;
  LOG_INFORMATION("event_count = " << event_count << "\n");

  LOG_INFORMATION("parse_EventList...\n");
  for (uint16_t i = 0; i < event_count; i++) {
    parse_andAddEvent(file, bufferHeader, eventAccumulator);
  }

}

LoadDNSEvent::BufferHeader LoadDNSEvent::parse_DataBufferHeader(VectorByteStream &file) {
  LOG_INFORMATION("parse_DataBufferHeader...\n")
  BufferHeader header = {};
  file.read<2>(header.bufferLength);
  file.extractDataChunk<2>()
        .readBits<1>(header.bufferType)
        .readBits<15>(header.bufferVersion);
  file.read<2>(header.headerLength);
  file.read<2>(header.bufferNumber);
  file.read<2>(header.runId);
  file.read<1>(header.mcpdId);
  file.extractDataChunk<1>()
        .skipBits<6>()
        .readBits<2>(header.deviceStatus);
  file.read<6>(header.timestamp);
  file.skip<24>();
  return header;

}


void LoadDNSEvent::parse_EndSignature(FileByteStream &file) {
  LOG_INFORMATION("parse_EndSignature...\n")
  const separator_t closing_sig = (0xFFFFAAAA55550000); // 0x00005555AAAAFFFF; //
  auto separator = file.read(separator_t());
  if (separator != closing_sig) {
    throw std::runtime_error(std::string("File Integrety LOST. (ugh!) 0x") + n2hexstr(separator)
                             + std::string("expected 0x") + n2hexstr(closing_sig));
  }
}

}// namespace Mantid
}// namespace DataHandling


