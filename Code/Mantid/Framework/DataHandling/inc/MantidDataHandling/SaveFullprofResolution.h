#ifndef MANTID_DATAHANDLING_SAVEFullprofRESOLUTION_H_
#define MANTID_DATAHANDLING_SAVEFullprofRESOLUTION_H_

#include "MantidKernel/System.h"
#include "MantidAPI/Algorithm.h"
#include "MantidDataObjects/TableWorkspace.h"

namespace Mantid
{
namespace DataHandling
{

  /** SaveFullprofResolution : TODO: DESCRIPTION
    
    Copyright &copy; 2012 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory

    This file is part of Mantid.

    Mantid is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    Mantid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    File change history is stored at: <https://github.com/mantidproject/mantid>
    Code Documentation is available at: <http://doxygen.mantidproject.org>
  */
  class DLLExport SaveFullprofResolution : public API::Algorithm
  {
  public:
    SaveFullprofResolution();
    virtual ~SaveFullprofResolution();

    /// Algorithm's name
    virtual const std::string name() const { return "SaveFullprofResolution"; }
    /// Algorithm's version
    virtual int version() const { return (1); }
    /// Algorithm's category for identification
    virtual const std::string category() const { return "Diffraction;DataHandling\\Text"; }

  private:
    /// Sets documentation strings for this algorithm
    virtual void initDocs();
    /// Initialisation code
    void init();
    ///Execution code
    void exec();
    ///Write the header information

    std::string toIRFString(int bankid);

    /// Parse input workspace to map of parameters
    void parseTableWorkspace();

    /// Map containing the name of value of each parameter required by .irf file
    std::map<std::string, double> mParameters;

    /// Input table workspace
    DataObjects::TableWorkspace_sptr inpWS;
    
  };


} // namespace DataHandling
} // namespace Mantid

#endif  /* MANTID_DATAHANDLING_SAVEFullprofRESOLUTION_H_ */
