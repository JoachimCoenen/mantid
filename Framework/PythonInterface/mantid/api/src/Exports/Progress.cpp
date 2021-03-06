// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
//     NScD Oak Ridge National Laboratory, European Spallation Source
//     & Institut Laue - Langevin
// SPDX - License - Identifier: GPL - 3.0 +
#include "MantidAPI/Progress.h"
#include "MantidAPI/Algorithm.h"

#include <boost/python/class.hpp>
#include <boost/python/init.hpp>

using Mantid::API::Algorithm;
using Mantid::API::Progress;
using Mantid::Kernel::ProgressBase;
using namespace boost::python;

void export_Progress() {
  class_<Progress, bases<ProgressBase>, boost::noncopyable>(
      "Progress",
      "Make a Progress object that is attached to the given algorithm, "
      "with progress between fractions [start,end] notifying a total of "
      "nreports times",
      init<Algorithm *, double, double, size_t>(
          (arg("alg"), arg("start"), arg("end"), arg("nreports"))));
}
