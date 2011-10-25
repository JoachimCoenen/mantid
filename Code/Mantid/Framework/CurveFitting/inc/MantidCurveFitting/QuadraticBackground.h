#ifndef MANTID_CURVEFITTING_QUADRATICBACKGROUND_H_
#define MANTID_CURVEFITTING_QUADRATICBACKGROUND_H_
/*WIKI*
Quadratic background
Y = A0 + A1*X + A2*X**2
*WIKI*/
    
#include "MantidKernel/System.h"
#include "MantidCurveFitting/BackgroundFunction.h"
#include <cmath>

namespace Mantid
{
namespace CurveFitting
{

  /** QuadraticBackground : Quadratic background as Y = A0 + A1*X + A2*X**2
    
    @author
    @date 2011-10-25

    Copyright &copy; 2011 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory

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

    File change history is stored at: <https://svn.mantidproject.org/mantid/trunk/Code/Mantid>
    Code Documentation is available at: <http://doxygen.mantidproject.org>
  */
  class DLLExport QuadraticBackground : public BackgroundFunction
  {
  public:
    QuadraticBackground();
    ~QuadraticBackground();
    
    std::string name()const{return "QuadraticBackground";}
    virtual void functionMW(double* out, const double* xValues, const size_t nData)const;
    virtual void functionDerivMW(API::Jacobian* out, const double* xValues, const size_t nData);

  private:
    void init();

  };


} // namespace CurveFitting
} // namespace Mantid

#endif  /* MANTID_CURVEFITTING_QUADRATICBACKGROUND_H_ */
