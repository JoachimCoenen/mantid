#ifndef MANTIDQTAPI_QWTWORKSPACESPECTRUMDATA_H
#define MANTIDQTAPI_QWTWORKSPACESPECTRUMDATA_H

#include "MantidAPI/MatrixWorkspace_fwd.h"
#include "DistributionOptions.h"
#include "MantidKernel/cow_ptr.h"
#include "MantidQtAPI/MantidQwtWorkspaceData.h"
#include "DllOption.h"

#include <boost/shared_ptr.hpp>
#include <QString>

//=================================================================================================
//=================================================================================================
/**  This class implements QwtData with direct access to a spectrum in a
 * MatrixWorkspace.
 */
class EXPORT_OPT_MANTIDQT_API QwtWorkspaceSpectrumData
    : public MantidQwtMatrixWorkspaceData {
public:
  QwtWorkspaceSpectrumData(const Mantid::API::MatrixWorkspace &workspace,
                           int specIndex, const bool logScale,
                           const bool plotAsDistribution);

  //! @return Pointer to a copy (virtual copy constructor)
  QwtWorkspaceSpectrumData *copy() const override;
  /// Return a new data object of the same type but with a new workspace
  QwtWorkspaceSpectrumData *copyWithNewSource(
      const Mantid::API::MatrixWorkspace &workspace) const override;

  //! @return Size of the data set
  size_t size() const override;

  /**
  Return the x value of data point i
  @param i :: Index
  @return x X value of data point i
  */
  double x(size_t i) const override;
  /**
  Return the y value of data point i
  @param i :: Index
  @return y Y value of data point i
  */
  double y(size_t i) const override;

  /// Returns the error of the i-th data point
  double e(size_t i) const override;
  /// Returns the x position of the error bar for the i-th data point (bin)
  double ex(size_t i) const override;
  /// Number of error bars to plot
  size_t esize() const override;

  double getYMin() const override;
  double getYMax() const override;
  /// Return the label to use for the X axis
  QString getXAxisLabel() const override;
  /// Return the label to use for the Y axis
  QString getYAxisLabel() const override;

  bool isHistogram() const { return m_isHistogram; }
  bool dataIsNormalized() const { return m_dataIsNormalized; }

  /// Inform the data that it is to be plotted on a log y scale
  void setLogScale(bool on) override;
  bool logScale() const override { return m_logScale; }
  void saveLowestPositiveValue(const double v) override;
  bool setAsDistribution(bool on = true);

  // Sets offsets for and enables waterfall plots
  void setXOffset(const double x) override;
  void setYOffset(const double y) override;
  void setWaterfallPlot(bool on) override;

protected:
  // Assignment operator (virtualized). MSVC not happy with compiler generated
  // one
  QwtWorkspaceSpectrumData &operator=(const QwtWorkspaceSpectrumData &);

private:
  friend class MantidMatrixCurve;

  /// Spectrum index in the workspace
  int m_spec;
  /// Copy of the X vector
  Mantid::MantidVec m_X;
  /// Copy of the Y vector
  Mantid::MantidVec m_Y;
  /// Copy of the E vector
  Mantid::MantidVec m_E;

  /// A caption for the X axis
  QString m_xTitle;
  /// A caption for the Y axis
  QString m_yTitle;

  /// Is the spectrum a histogram?
  bool m_isHistogram;
  /// If true the data already has the bin widths divided in
  bool m_dataIsNormalized;
  /// This field can be set true for a histogram workspace. If it's true x(i)
  /// returns (X[i]+X[i+1])/2
  bool m_binCentres;
  /// Indicates that the data is plotted on a log y scale
  bool m_logScale;
  /// lowest y value
  double m_minY;
  /// lowest positive y value
  double m_minPositive;
  /// higest y value
  double m_maxY;
  /// Is plotting as distribution
  bool m_isDistribution;

  /// Indicates whether or not waterfall plots are enabled
  bool m_isWaterfall;

  /// x-axis offset for waterfall plots
  double m_offsetX;

  /// y-axis offset for waterfall plots
  double m_offsetY;
};
#endif
