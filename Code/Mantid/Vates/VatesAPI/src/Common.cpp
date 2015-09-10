#include "MantidVatesAPI/Common.h"
#include "MantidGeometry/MDGeometry/IMDDimension.h"
#include "MantidKernel/UnitLabel.h"

#include <vtkNew.h>
#include <vtkFieldData.h>
#include <vtkStringArray.h>

#include "vtkPVChangeOfBasisHelper.h"

#include <boost/math/special_functions/fpclassify.hpp>
#include <boost/regex.hpp>

// using namespace Mantid::Geometry;
namespace Mantid {
namespace VATES {
std::string makeAxisTitle(Dimension_const_sptr dim) {
  // The UnitLabels which are stored in old files don't necessarily contain
  // valid Latex symbols. We check if there is a difference between the ASCII
  // and the Latex symbols, if there is one, then use the Latex else modify
  // the ASCII version to display Latex

  auto latexSymbol = dim->getMDUnits().getUnitLabel().latex();
  auto asciiSymbol = dim->getMDUnits().getUnitLabel().ascii();
  auto hasLatexSymbol = asciiSymbol != latexSymbol ? true: false;
  std::string symbol;

  if (!hasLatexSymbol) {
    symbol = convertAxesTitleToLatex(latexSymbol);
  } else {
    symbol = latexSymbol;
  }

  std::string title = dim->getName();
  title += " ($";
  title += symbol;
  title += "$)";
  return title;
}

std::string convertAxesTitleToLatex(std::string toConvert) {
  std::string converted;

  // Check if the input has a unit of A\\^-1: this is converted to \\\\AA^{-1}
  // else
  // Check if the input has a unit of Ang: this is convered to \\\\AA
  // else leave as it is
  if (toConvert.find("A^-1") != std::string::npos) {
    boost::regex re("A\\^-1");
    converted = boost::regex_replace(toConvert, re, "\\\\AA^{-1}");
  } else if (toConvert.find("Ang") != std::string::npos) {
    boost::regex re("Ang");
    converted = boost::regex_replace(toConvert, re, "\\\\AA");
  } else {
    converted = toConvert;
  }
  return converted;
}

void setAxisLabel(std::string metadataLabel, std::string labelString,
                  vtkFieldData *fieldData) {
  vtkNew<vtkStringArray> axisTitle;
  axisTitle->SetName(metadataLabel.c_str());
  axisTitle->SetNumberOfComponents(1);
  axisTitle->SetNumberOfTuples(1);
  axisTitle->SetValue(0, labelString.c_str());
  fieldData->AddArray(axisTitle.GetPointer());
}

bool isSpecial(double value) {
  return boost::math::isnan(value) || boost::math::isinf(value);
}

} // VATES
} // Mantid
