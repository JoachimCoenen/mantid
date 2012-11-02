#ifndef MANTID_ALGORITHMS_GENERATEPYTHONSCRIPT_H_
#define MANTID_ALGORITHMS_GENERATEPYTHONSCRIPT_H_

#include "MantidKernel/System.h"
#include "MantidAPI/Algorithm.h"

namespace Mantid
{
namespace Algorithms
{

/** GeneratePythonScript : TODO: DESCRIPTION

  An Algorithm to generate a Python script file to reproduce the history of a workspace.

  Properties:
  <ul>
  <li>Filename - the name of the file to write to. </li>
  <li>InputWorkspace - the workspace name who's history is to be saved.</li>
  </ul>

  @author Peter G Parker, ISIS, RAL
  @date 2011-09-13

  Copyright &copy; 2011 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory

  This file is part of Mantid.

  Mantid is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  (at your option) any later version.

  Mantid is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program. If not, see <http://www.gnu.org/licenses/>.

  File change history is stored at: <https://github.com/mantidproject/mantid>
  Code Documentation is available at: <http://doxygen.mantidproject.org>
*/
class DLLExport GeneratePythonScript : public API::Algorithm
{
public:
  GeneratePythonScript() : Mantid::API::Algorithm() {}
  virtual ~GeneratePythonScript() {}

  /// Algorithm's name for identification
  virtual const std::string name() const { return "GeneratePythonScript";};
  /// Algorithm's version for identification
  virtual int version() const { return 1;};
  /// Algorithm's category for identification
  virtual const std::string category() const { return "Utility;PythonAlgorithms";}

protected:
  /// Sets documentation strings for this algorithm
  virtual void initDocs();
  /// Initialise the properties
  void init();
  /// Run the algorithm
  void exec();
  /// Generate the line of script corresponding to the given AlgorithmHistory
  std::string genAlgString(const API::AlgorithmHistory&);
  /// Generate the parameter string (of format "[name]='[value]'") for the given PropertyHistory.
  std::string genParamString(const Kernel::PropertyHistory&, const API::IAlgorithm_sptr, const std::string algHistName);
  // "Sanitize" property name.
  std::string sanitizePropertyName(const std::string&);
};


} // namespace Algorithms
} // namespace Mantid

#endif /* MANTID_ALGORITHMS_GENERATEPYTHONSCRIPT_H_ */
