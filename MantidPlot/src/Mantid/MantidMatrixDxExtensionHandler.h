// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
//     NScD Oak Ridge National Laboratory, European Spallation Source
//     & Institut Laue - Langevin
// SPDX - License - Identifier: GPL - 3.0 +
#ifndef MANTIDPLOT_MANTIDMATRIXDXEXTENSIONHANDLER_H
#define MANTIDPLOT_MANTIDMATRIXDXEXTENSIONHANDLER_H

#include "IMantidMatrixExtensionHandler.h"
#include "MantidMatrixModel.h"
#include "MantidMatrixTabExtension.h"

class MantidMatrixDxExtensionHandler : public IMantidMatrixExtensionHandler {
public:
  MantidMatrixDxExtensionHandler();
  ~MantidMatrixDxExtensionHandler() override;
  void setNumberFormat(MantidMatrixTabExtension &extension, const QChar &format,
                       int precision) override;
  void recordFormat(MantidMatrixTabExtension &extension, const QChar &format,
                    int precision) override;
  QChar getFormat(MantidMatrixTabExtension &extension) override;
  int getPrecision(MantidMatrixTabExtension &extension) override;
  void setColumnWidth(MantidMatrixTabExtension &extension, int width,
                      int numberOfColumns) override;
  int getColumnWidth(MantidMatrixTabExtension &extension) override;
  QTableView *getTableView(MantidMatrixTabExtension &extension) override;
  void setColumnWidthPreference(MantidMatrixTabExtension &extension,
                                int width) override;
  int getColumnWidthPreference(MantidMatrixTabExtension &extension) override;

private:
  MantidMatrixModel::Type m_type;
};
#endif