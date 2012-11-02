#ifndef IMDDIMENSIONFACTORY_H_
#define IMDDIMENSIONFACTORY_H_ 

/**
*  IMDDimensionFactory. Handles conversion of dimension xml to IMDDimension objects.
*
*  This algorithm performs dynamic rebinning driven by the xml string passed as an input.
*
*  @date 10/02/2011
*  @author Owen Arnold
*
*  Copyright &copy; 2010 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory
*
*  This file is part of Mantid.
*
*  Mantid is free software; you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation; either version 3 of the License, or
*  (at your option) any later version.
*
*  Mantid is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
*  File change history is stored at: <https://github.com/mantidproject/mantid>
*  Code Documentation is available at: <http://doxygen.mantidproject.org>
*/

#include "MantidGeometry/MDGeometry/IMDDimension.h"

namespace Poco
{
namespace XML
{
class Element;
}
}

namespace Mantid
{
namespace Geometry
{
class MDHistoDimension;
class MANTID_GEOMETRY_DLL IMDDimensionFactory
{

public:

  /// Constructor
  IMDDimensionFactory(Poco::XML::Element* dimensionXML);

  /// Constructor
  IMDDimensionFactory(const IMDDimensionFactory& other);

  /// Assignment operator
  IMDDimensionFactory& operator=(const IMDDimensionFactory& other);

  /// Alternate Constructional method.
  static IMDDimensionFactory createDimensionFactory(const std::string& xmlString);

  /// Destructor
  ~IMDDimensionFactory();

  /// Factory method.
  IMDDimension* create() const;

  /// Factory method.
  IMDDimension* create(int nBins, double min, double max) const;

private:

  IMDDimensionFactory();

  void setXMLString(const std::string& xmlString);

  /// Internal creation method.
  MDHistoDimension* doCreate() const;

  /// Dimension xml to process.
  Poco::XML::Element* m_dimensionXML;
};

  
MANTID_GEOMETRY_DLL Mantid::Geometry::IMDDimension_sptr createDimension(const std::string& dimensionXMLString);

MANTID_GEOMETRY_DLL Mantid::Geometry::IMDDimension_sptr createDimension(const std::string& dimensionXMLString, int nBins, double min, double max);

}
}

#endif
