//----------------------------------------------------------------------
// Includes
//----------------------------------------------------------------------
#include "MantidAPI/FileFinder.h"
#include "MantidKernel/ConfigService.h"
#include "MantidKernel/FacilityInfo.h"
#include "MantidKernel/InstrumentInfo.h"

#include "Poco/Path.h"
#include "Poco/File.h"
#include "Poco/StringTokenizer.h"
#include <boost/lexical_cast.hpp>

#include <cctype>
#include <algorithm>

namespace Mantid
{
  namespace API
  {
    //----------------------------------------------------------------------
    // Public member functions
    //----------------------------------------------------------------------
    /**
     * Default constructor
     */
    FileFinderImpl::FileFinderImpl()
    {
    }

    /**
      * Return the full path to the file given its name
      * @param fName A full file name (without path) including extension
      * @return The full path if the file exists and can be found in one of the search locations
      *  or an empty string otherwise.
      */
    std::string FileFinderImpl::getFullPath(const std::string& fName)const
    {
      const std::vector<std::string>& searchPaths = Kernel::ConfigService::Instance().getDataSearchDirs();
      std::vector<std::string>::const_iterator it = searchPaths.begin();
      for(;it != searchPaths.end(); ++it)
      {
        Poco::Path path(*it,fName);
        Poco::File file(path);
        if (file.exists())
        {
          return path.toString();
        }
      }
      return "";
    }

    /**
      * Extracts the instrument name and run number from a hint
      * @param hint The name hint
      * @return A pair of instrument name and run number
      */
    std::pair<std::string,std::string> FileFinderImpl::toInstrumentAndNumber(const std::string& hint)const
    {
      std::string instrPart;
      std::string runPart;

      if (isdigit(hint[0]))
      {
        instrPart = Kernel::ConfigService::Instance().Facility().Instrument().shortName();
        runPart = hint;
      }
      else
      {
        std::string::const_iterator it = std::find_if(hint.begin(),hint.end(),isdigit);
        if (it == hint.end())
        {
          throw std::invalid_argument("Malformed hint to FileFinderImpl::makeFileName: "+hint);
        }
        std::string::size_type i = it - hint.begin();
        instrPart = hint.substr(0,i);
        runPart = hint.substr(i);
      }

      Kernel::InstrumentInfo instr = Kernel::ConfigService::Instance().Facility().Instrument(instrPart);
      int nZero = instr.zeroPadding();
      // remove any leading zeros in case there are too many of them
      std::string::size_type i = runPart.find_first_not_of('0');
      runPart.erase(0,i);
      while(runPart.size() < nZero) runPart.insert(0,"0");
      if (runPart.size() > nZero)
      {
        throw std::invalid_argument("Run number does not match instrument's zero padding");
      }
      instrPart = instr.shortName();

      return std::make_pair(instrPart,runPart);

    }

    /**
      * Make a data file name (without extension) from a hint. The hint can be either a run number or
      * a run number prefixed with an instrument name/short name. If the instrument 
      * name is absent the default one is used.
      * @param hint The name hint
      * @return The file name
      * @throws NotFoundError if a required default is not set
      * @thorws std::invalid_argument if the argument is malformed or run number is too long
      */
    std::string FileFinderImpl::makeFileName(const std::string& hint)const
    {
      if (hint.empty()) return "";

      std::pair<std::string,std::string> p = toInstrumentAndNumber(hint);
      return p.first + p.second;
    }

    /**
      * Find the file given a hint. Calls makeFileName internally.
      * @param hint The name hint
      * @return The full path to the file or empty string if not found
      */
    std::string FileFinderImpl::findFile(const std::string& hint)const
    {
      std::string fName = makeFileName(hint);
      const std::vector<std::string> exts = Kernel::ConfigService::Instance().Facility().extensions();
      std::vector<std::string>::const_iterator ext = exts.begin();
      for(;ext != exts.end(); ++ext)
      {
        std::string path = getFullPath(fName + "." + *ext);
        if ( !path.empty() ) return path;
      }
      return "";
    }

    /**
      * Find a list of files file given a hint. Calls findFile internally.
      * @param hint Comma separated list of hints to findFile method. 
      *  Can also include ranges of runs, e.g. 123-135 or equivalently 123-35.
      *  Only the beginning of a range can contain an instrument name.
      * @return A vector of full paths or empty vector
      * @thorws std::invalid_argument if the argument is malformed 
      */
    std::vector<std::string> FileFinderImpl::findFiles(const std::string& hint)const
    {
      std::vector<std::string> res;
      Poco::StringTokenizer hints(hint, ",", Poco::StringTokenizer::TOK_TRIM | Poco::StringTokenizer::TOK_IGNORE_EMPTY);
      Poco::StringTokenizer::Iterator h = hints.begin();

      for(; h != hints.end(); ++h)
      {
        Poco::StringTokenizer range(*h, "-", Poco::StringTokenizer::TOK_TRIM | Poco::StringTokenizer::TOK_IGNORE_EMPTY);
        if (range.count() > 2)
        {
          throw std::invalid_argument("Malformed range of runs: "+*h);
        }
        else if (range.count() == 2)
        {
          std::pair<std::string,std::string> p1 = toInstrumentAndNumber(range[0]);
          std::string run = p1.second;
          int nZero = run.size(); // zero padding
          if (range[1].size() > nZero)
          {
            ("Malformed range of runs: "+*h + 
              ". The end of string value is longer than the instrument's zero padding");
          }
          int runNumber = boost::lexical_cast<int>(run);
          std::string runEnd = run;
          runEnd.replace(runEnd.end()-range[1].size(),runEnd.end(),range[1]);
          int runEndNumber = boost::lexical_cast<int>(runEnd);
          if (runEndNumber < runNumber)
          {
            throw std::invalid_argument("Malformed range of runs: "+*h);
          }
          for(int irun = runNumber; irun <= runEndNumber; ++irun)
          {
            run = boost::lexical_cast<std::string>(irun);
            while(run.size() < nZero) run.insert(0,"0");
            std::string path = findFile(p1.first + run);
            if ( !path.empty() )
            {
              res.push_back(path);
            }
          }
        }
        else
        {
          std::string path = findFile(*h);
          if ( !path.empty() )
          {
            res.push_back(path);
          }
        }
      }

      return res;
    }

  }// API
  
}// Mantid

