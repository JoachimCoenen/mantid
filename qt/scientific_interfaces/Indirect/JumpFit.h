// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
//     NScD Oak Ridge National Laboratory, European Spallation Source
//     & Institut Laue - Langevin
// SPDX - License - Identifier: GPL - 3.0 +
#ifndef MANTIDQTCUSTOMINTERFACES_JUMPFIT_H_
#define MANTIDQTCUSTOMINTERFACES_JUMPFIT_H_

#include "IndirectFitAnalysisTab.h"
#include "JumpFitModel.h"
#include "ui_JumpFit.h"

#include "MantidAPI/IFunction.h"
#include "MantidAPI/TextAxis.h"

namespace MantidQt {
namespace CustomInterfaces {
namespace IDA {
class DLLExport JumpFit : public IndirectFitAnalysisTab {
  Q_OBJECT

public:
  JumpFit(QWidget *parent = nullptr);

  void setupFitTab() override;

protected slots:
  void updatePlotOptions() override;
  void updateModelFitTypeString();
  void plotClicked();
  void runClicked();

protected:
  void setRunIsRunning(bool running) override;
  void setFitSingleSpectrumIsFitting(bool fitting) override;
  void setPlotResultEnabled(bool enabled) override;
  void setSaveResultEnabled(bool enabled) override;

private slots:
  void updateAvailableFitTypes();

private:
  void addFunctions(std::vector<std::string> const &functions);

  void setPlotResultIsPlotting(bool plotting);
  void setButtonsEnabled(bool enabled);
  void setRunEnabled(bool enabled);
  void setFitSingleSpectrumEnabled(bool enabled);

  JumpFitModel *m_jumpFittingModel;
  std::unique_ptr<Ui::JumpFit> m_uiForm;
};
} // namespace IDA
} // namespace CustomInterfaces
} // namespace MantidQt

#endif
