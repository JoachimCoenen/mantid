#include "MantidMDAlgorithms/ReflectometryTransformKiKf.h"
#include "MantidDataObjects/MDEventWorkspace.h"
#include "MantidGeometry/MDGeometry/MDHistoDimension.h"
#include "MantidDataObjects/Workspace2D.h"
#include <stdexcept>

using namespace Mantid::API;
using namespace Mantid::DataObjects;
using namespace Mantid::Kernel;
using namespace Mantid::Geometry;

namespace Mantid {
namespace MDAlgorithms {

/*
  Constructor
  @param kiMin: min ki value (extent)
  @param kiMax: max ki value (extent)
  @param kfMin: min kf value (extent)
  @param kfMax; max kf value (extent)
  @param incidentTheta: Predetermined incident theta value
  @param numberOfBinsQx: Number of bins in the qx axis
  @param numberOfBinsQz: Number of bins in the qz axis
*/
ReflectometryTransformKiKf::ReflectometryTransformKiKf(
    double kiMin, double kiMax, double kfMin, double kfMax,
    double incidentTheta, int numberOfBinsQx, int numberOfBinsQz)
    : ReflectometryTransform(kiMin, kiMax, kfMin, kfMax, numberOfBinsQx,
                             numberOfBinsQz),
      m_KiCalculation(incidentTheta) {
  if (incidentTheta < 0 || incidentTheta > 90) {
    throw std::out_of_range("incident theta angle must be > 0 and < 90");
  }
}

//----------------------------------------------------------------------------------------------
/** Destructor
 */
ReflectometryTransformKiKf::~ReflectometryTransformKiKf() {}

/*
  Execute the transformtion. Generates an output IMDEventWorkspace.
  @return the constructed IMDEventWorkspace following the transformation.
  @param ws: Input MatrixWorkspace const shared pointer
  @param boxController: box controller to apply on output workspace.
*/
Mantid::API::IMDEventWorkspace_sptr ReflectometryTransformKiKf::executeMD(
    Mantid::API::MatrixWorkspace_const_sptr inputWs,
    BoxController_sptr boxController) const {
  MDHistoDimension_sptr kiDim = MDHistoDimension_sptr(new MDHistoDimension(
      "Ki", "ki", "(Ang^-1)", static_cast<Mantid::coord_t>(m_d0Min),
      static_cast<Mantid::coord_t>(m_d0Max), m_d0NumBins));
  MDHistoDimension_sptr kfDim = MDHistoDimension_sptr(new MDHistoDimension(
      "Kf", "kf", "(Ang^-1)", static_cast<Mantid::coord_t>(m_d1Min),
      static_cast<Mantid::coord_t>(m_d1Max), m_d1NumBins));

  auto ws = createMDWorkspace(kiDim, kfDim, boxController);

  auto spectraAxis = inputWs->getAxis(1);
  for (size_t index = 0; index < inputWs->getNumberHistograms(); ++index) {
    auto counts = inputWs->readY(index);
    auto wavelengths = inputWs->readX(index);
    auto errors = inputWs->readE(index);
    const size_t nInputBins = wavelengths.size() - 1;
    const double theta_final = spectraAxis->getValue(index);
    CalculateReflectometryK kfCalculation(theta_final);
    // Loop over all bins in spectra
    for (size_t binIndex = 0; binIndex < nInputBins; ++binIndex) {
      const double &wavelength =
          0.5 * (wavelengths[binIndex] + wavelengths[binIndex + 1]);
      double _ki = m_KiCalculation.execute(wavelength);
      double _kf = kfCalculation.execute(wavelength);
      double centers[2] = {_ki, _kf};

      ws->addEvent(MDLeanEvent<2>(float(counts[binIndex]),
                                  float(errors[binIndex] * errors[binIndex]),
                                  centers));
    }
  }
  ws->splitAllIfNeeded(NULL);
  ws->refreshCache();
  return ws;
}

/**
 *
 * @param inputWs : Input Matrix workspace
 * @return workspace group containing output matrix workspaces of ki and kf
 */
Mantid::API::MatrixWorkspace_sptr ReflectometryTransformKiKf::execute(
    Mantid::API::MatrixWorkspace_const_sptr inputWs) const {
  auto ws = boost::make_shared<Mantid::DataObjects::Workspace2D>();

  ws->initialize(m_d1NumBins, m_d0NumBins,
                 m_d0NumBins); // Create the output workspace as a distribution

  // Mapping so that ki and kf values calculated can be added to the matrix
  // workspace at the correct index.
  const double gradKi =
      double(m_d0NumBins) / (m_d0Max - m_d0Min); // The x - axis
  const double gradKf =
      double(m_d1NumBins) / (m_d1Max - m_d1Min); // Actually the y-axis
  const double cxToIndex = -gradKi * m_d0Min;
  const double czToIndex = -gradKf * m_d1Min;
  const double cxToKi = m_d0Min - (1 / gradKi);
  const double czToKf = m_d1Min - (1 / gradKf);

  // Create an X - Axis.
  MantidVec xAxisVec =
      createXAxis(ws.get(), gradKi, cxToKi, m_d0NumBins, "ki", "1/Angstroms");
  // Create a Y (vertical) Axis
  createVerticalAxis(ws.get(), xAxisVec, gradKf, czToKf, m_d1NumBins, "kf",
                     "1/Angstroms");

  // Loop over all entries in the input workspace and calculate ki and kf for
  // each.
  auto spectraAxis = inputWs->getAxis(1);
  for (size_t index = 0; index < inputWs->getNumberHistograms(); ++index) {
    auto counts = inputWs->readY(index);
    auto wavelengths = inputWs->readX(index);
    auto errors = inputWs->readE(index);
    const size_t nInputBins = wavelengths.size() - 1;
    const double theta_final = spectraAxis->getValue(index);
    CalculateReflectometryK kfCalculation(theta_final);
    // Loop over all bins in spectra
    for (size_t binIndex = 0; binIndex < nInputBins; ++binIndex) {
      const double wavelength =
          0.5 * (wavelengths[binIndex] + wavelengths[binIndex + 1]);
      double _ki = m_KiCalculation.execute(wavelength);
      double _kf = kfCalculation.execute(wavelength);

      if (_ki >= m_d0Min && _ki <= m_d0Max && _kf >= m_d1Min &&
          _kf <= m_d1Max) // Check that the calculated ki and kf are in range
      {
        const int outIndexX = (int)((gradKi * _ki) + cxToIndex);
        const int outIndexZ = (int)((gradKf * _kf) + czToIndex);

        ws->dataY(outIndexZ)[outIndexX] += counts[binIndex];
        ws->dataE(outIndexZ)[outIndexX] += errors[binIndex];
      }
    }
  }
  return ws;
}

} // namespace Mantid
} // namespace MDAlgorithms
