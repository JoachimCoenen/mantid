#include "MantidTestHelpers/IndirectFitDataCreationHelper.h"
#include "MantidTestHelpers/WorkspaceCreationHelper.h"

namespace Mantid {
namespace IndirectFitDataCreationHelper {
using namespace Mantid::API;

MatrixWorkspace_sptr createWorkspace(int const &numberOfSpectra) {
  return WorkspaceCreationHelper::create2DWorkspace(numberOfSpectra, 10);
}

MatrixWorkspace_sptr createInstrumentWorkspace(int const &xLength,
                                               int const &yLength) {
  return WorkspaceCreationHelper::create2DWorkspaceWithFullInstrument(
      xLength, yLength - 1, false, false, true, "testInst");
}

MatrixWorkspace_sptr
createWorkspaceWithTextAxis(int const &numberOfSpectra,
                            std::vector<std::string> const &labels) {
  if (static_cast<std::size_t>(numberOfSpectra) == labels.size()) {
    auto workspace = createWorkspace(numberOfSpectra);
    workspace->replaceAxis(1, getTextAxis(numberOfSpectra, labels));
    return workspace;
  } else
    throw std::runtime_error(
        "The number of spectra is not equal to the number of labels");
}

TextAxis *getTextAxis(int const &numberOfSpectra,
                      std::vector<std::string> const &labels) {
  auto axis = new TextAxis(numberOfSpectra);
  for (auto index = 0; index < numberOfSpectra; ++index)
    axis->setLabel(index, labels[index]);
  return axis;
}

MatrixWorkspace_sptr setWorkspaceEFixed(MatrixWorkspace_sptr workspace,
                                        int const &xLength) {
  for (int i = 0; i < xLength; ++i)
    workspace->setEFixed((i + 1), 0.50);
  return workspace;
}

MatrixWorkspace_sptr
setWorkspaceBinEdges(MatrixWorkspace_sptr workspace, int const &yLength,
                     Mantid::HistogramData::BinEdges const &binEdges) {
  for (int i = 0; i < yLength; ++i)
    workspace->setBinEdges(i, binEdges);
  return workspace;
}

MatrixWorkspace_sptr setWorkspaceBinEdges(MatrixWorkspace_sptr workspace,
                                          int const &xLength,
                                          int const &yLength) {
  Mantid::HistogramData::BinEdges binEdges(xLength - 1, 0.0);
  int j = 0;
  std::generate(begin(binEdges), end(binEdges),
                [&j] { return 0.5 + 0.75 * ++j; });
  setWorkspaceBinEdges(workspace, yLength, binEdges);
  return workspace;
}

MatrixWorkspace_sptr setWorkspaceProperties(MatrixWorkspace_sptr workspace,
                                            int const &xLength,
                                            int const &yLength) {
  setWorkspaceBinEdges(workspace, xLength, yLength);
  setWorkspaceEFixed(workspace, xLength);
  return workspace;
}

MatrixWorkspace_sptr createWorkspaceWithInstrument(int const &xLength,
                                                   int const &yLength) {
  auto workspace = createInstrumentWorkspace(xLength, yLength);
  workspace->initialize(yLength, xLength, xLength - 1);
  return setWorkspaceProperties(workspace, xLength, yLength);
}

} // namespace IndirectFitDataCreationHelper
} // namespace Mantid
