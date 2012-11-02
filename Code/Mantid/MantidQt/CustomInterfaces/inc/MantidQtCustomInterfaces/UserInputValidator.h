#ifndef MANTID_CUSTOMINTERFACES_USERINPUTVALIDATOR_H_
#define MANTID_CUSTOMINTERFACES_USERINPUTVALIDATOR_H_

#include "MantidQtMantidWidgets/WorkspaceSelector.h"
#include "MantidQtMantidWidgets/MWRunFiles.h"

using MantidQt::MantidWidgets::WorkspaceSelector;
using MantidQt::MantidWidgets::MWRunFiles;

class QLineEdit;
class QLabel;
class QString;
class QStringList;

namespace MantidQt
{
  namespace CustomInterfaces
  {
    /**
     * (Currently used in C2E-Indirect and IDA.)
     *
     * A class to try and get rid of some of the boiler-plate code surrounding input validation,
     * and hopefully as a result make it more readable.
     *
     * It has as its state a QStringList, which are the accumulated error messages after multiple
     * calls to its "check[...]" member-functions.
     *
     * Copyright &copy; 2007-8 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory
     *
     * This file is part of Mantid.
     *
     * Mantid is free software; you can redistribute it and/or modify
     * it under the terms of the GNU General Public License as published by
     * the Free Software Foundation; either version 3 of the License, or
     * (at your option) any later version.
     *
     * Mantid is distributed in the hope that it will be useful,
     * but WITHOUT ANY WARRANTY; without even the implied warranty of
     * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     * GNU General Public License for more details.
     *
     * You should have received a copy of the GNU General Public License
     * along with this program.  If not, see <http://www.gnu.org/licenses/>.
     *
     * File change history is stored at: <https://github.com/mantidproject/mantid>.
     * Code Documentation is available at: <http://doxygen.mantidproject.org>
     */
    class UserInputValidator
    {
    public:
      /// Default Constructor.
      UserInputValidator();

      /// Check that the given QLineEdit field is not empty.
      void checkFieldIsNotEmpty(const QString & name, QLineEdit * field, QLabel * errorLabel);
      /// Check that the given QLineEdit field is valid as per any validators it might have.
      void checkFieldIsValid(const QString & errorMessage, QLineEdit * field, QLabel * errorLabel);
      /// Check that the given WorkspaceSelector is not empty.
      void checkWorkspaceSelectorIsNotEmpty(const QString & name, WorkspaceSelector * workspaceSelector);
      /// Check that the given MWRunFiles widget has valid files.
      void checkMWRunFilesIsValid(const QString & name, MWRunFiles * widget);
      /// Check that the given start and end range is valid.
      void checkValidRange(const QString & name, std::pair<double, double> range);
      /// Check that the given ranges dont overlap.
      void checkRangesDontOverlap(std::pair<double, double> rangeA, std::pair<double, double> rangeB);
      /// Check that the given "outer" range completely encloses the given "inner" range.
      void checkRangeIsEnclosed(const QString & outerName, std::pair<double, double> outer, const QString & innerName, std::pair<double, double> inner);
      /// Check that the given range can be split evenly into bins of the given width.
      void checkBins(double lower, double binWidth, double upper, double tolerance = 0.00000001);
      /// Add a custom error message to the list.
      void addErrorMessage(const QString & message);

      /// Returns an error message which contains all the error messages raised by the check functions.
      QString generateErrorMessage();

    private:
      /// Any raised error messages.
      QStringList m_errorMessages;
    };
  }
}

#endif // MANTID_CUSTOMINTERFACES_USERINPUTVALIDATOR_H_