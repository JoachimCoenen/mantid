#include "MantidQtMantidWidgets/MuonFitDataView.h"
#include <stdexcept>

namespace MantidQt {
namespace MantidWidgets {

/**
 * Constructor for the widget
 * @param parent :: [input] Parent dialog for the widget
 * @param runNumber :: [input] Run number of initial workspace
 * @param instName :: [input] Name of instrument from initial workspace
 * @param numPeriods :: [input] Number of periods from initial workspace
 * @param groups :: [input] Group names from initial workspace
 */
MuonFitDataView::MuonFitDataView(QWidget *parent, int runNumber,
                                 const QString &instName, size_t numPeriods,
                                 const QStringList &groups)
    : MantidWidget(parent) {
  m_ui.setupUi(this);
  this->setUpValidators();
  this->setDefaultValues();
  this->setWorkspaceDetails(runNumber, instName);
  m_presenter = Mantid::Kernel::make_unique<MuonFitDataPresenter>(this);
  m_presenter->setNumPeriods(numPeriods);
  m_presenter->setAvailableGroups(groups);
  // TODO: connect signals and slots here
}

/**
 * Get the user's supplied workspace index (default 0)
 * Returns an unsigned int so it can be put into a QVariant
 * @returns :: Workspace index input by user
 */
unsigned int MuonFitDataView::getWorkspaceIndex() const {
  // Validator ensures this can be cast to a positive integer
  const QString index = m_ui.txtWSIndex->text();
  return index.toUInt();
}

/**
 * Set the workspace index in the UI
 * @param index :: [input] Workspace index to set
 */
void MuonFitDataView::setWorkspaceIndex(unsigned int index) {
  m_ui.txtWSIndex->setText(QString::number(index));
}

/**
 * Get the user's supplied start time (default 0)
 * @returns :: start time input by user in microseconds
 */
double MuonFitDataView::getStartTime() const {
  // Validator ensures cast to double will succeed
  const QString start = m_ui.txtStart->text();
  return start.toDouble();
}

/**
 * Set the start time in the UI
 * @param start :: [input] Start time in microseconds
 */
void MuonFitDataView::setStartTime(double start) {
  m_ui.txtStart->setText(QString::number(start));
}

/**
 * Get the user's supplied end time (default 10)
 * @returns :: start time input by user in microseconds
 */
double MuonFitDataView::getEndTime() const {
  // Validator ensures cast to double will succeed
  const QString end = m_ui.txtEnd->text();
  return end.toDouble();
}

/**
 * Set the end time in the UI
 * @param end :: [input] End time in microseconds
 */
void MuonFitDataView::setEndTime(double end) {
  m_ui.txtEnd->setText(QString::number(end));
}

/**
 * Get the filenames of the supplied run numbers
 * @returns :: list of run filenames
 */
QStringList MuonFitDataView::getRuns() const {
  // Run file search in case anything's changed
  m_ui.runs->findFiles();
  // Wait for file search to finish.
  while (m_ui.runs->isSearching()) {
    QApplication::processEvents();
  }
  return m_ui.runs->getFilenames();
}

/**
 * Set up input validation on UI controls
 * e.g. some boxes should only accept numeric input
 */
void MuonFitDataView::setUpValidators() {
  // WS index: non-negative integers only
  m_ui.txtWSIndex->setValidator(new QIntValidator(0, 1000, this));
  // Start/end times: numeric values only
  m_ui.txtStart->setValidator(new QDoubleValidator(this));
  m_ui.txtEnd->setValidator(new QDoubleValidator(this));
}

/**
 * Set up run finder with initial run number and instrument
 * @param runNumber :: [input] Run number from loaded workspace
 * @param instName :: [input] Instrument name from loaded workspace
 */
void MuonFitDataView::setWorkspaceDetails(int runNumber,
                                          const QString &instName) {
  // Set initial run to be run number of the workspace loaded in Home tab
  m_ui.runs->setText(QString::number(runNumber) + "-");
  // Set the file finder to the correct instrument (not Mantid's default)
  m_ui.runs->setInstrumentOverride(instName);
}

/**
 * Set default values in some input controls
 * Defaults copy those previously used in muon fit property browser
 */
void MuonFitDataView::setDefaultValues() {
  m_ui.lblStart->setText(QString("Start (%1s)").arg(QChar(0x03BC)));
  m_ui.lblEnd->setText(QString("End (%1s)").arg(QChar(0x03BC)));
  this->setWorkspaceIndex(0);
  this->setStartTime(0.0);
  this->setEndTime(0.0);
}

/**
 * Set visibility of the "Periods" group box
 * (if single-period, hide to not confuse the user)
 * @param visible :: [input] Whether to show or hide the options
 */
void MuonFitDataView::setPeriodVisibility(bool visible) {
  m_ui.groupBoxPeriods->setVisible(visible);
}

/**
 * Add a new checkbox to the list of groups with given name
 * @param name :: [input] Name of group to add
 */
void MuonFitDataView::addGroupCheckbox(const QString &name) {
  Q_UNUSED(name)
  throw std::runtime_error("Not implemented yet");
}

/**
 * Clears all group names and checkboxes
 * (ready to add new ones)
 */
void MuonFitDataView::clearGroupCheckboxes() {
  throw std::runtime_error("Not implemented yet");
}

/**
 * Checks if the given group has been selected or not
 * @param name :: [input] Name of group to test
 * @returns :: Whether checkbox was selected by user
 */
bool MuonFitDataView::isGroupSelected(const QString &name) const {
  Q_UNUSED(name)
  throw std::runtime_error("Not implemented yet");
}

/**
 * Set selection state of given group
 * @param name :: [input] Name of group to select/deselect
 * @param selected :: [input] True to select, false to deselect
 */
void MuonFitDataView::setGroupSelected(const QString &name, bool selected) {
  Q_UNUSED(name)
  Q_UNUSED(selected)
  throw std::runtime_error("Not implemented yet");
}

/**
 * Called by presenter. Sets checkboxes on UI for given number
 * of periods plus "combination" boxes.
 * @param numPeriods :: [input] Number of periods
 */
void MuonFitDataView::setNumPeriods(size_t numPeriods) {
  Q_UNUSED(numPeriods)
  throw std::runtime_error("Not implemented yet");
}

/**
 * Returns a list of periods and combinations chosen in UI
 * @returns :: list of periods e.g. "1", "3", "1+2-3+4"
 */
QStringList MuonFitDataView::getPeriodSelections() const {
  throw std::runtime_error("Not implemented yet");
}

/**
*Gets user input in the form of a QVariant
*
*This is implemented as the "standard" way of getting input from a
*MantidWidget. In practice it is probably easier to get the input
*using other methods.
*
*The returned QVariant is a QVariantMap of (parameter, value) pairs.
*@returns :: QVariant containing a QVariantMap
*/
QVariant MuonFitDataView::getUserInput() const {
  QVariant ret;
  auto map = ret.asMap();
  map.insert("Workspace index", getWorkspaceIndex());
  map.insert("Start", getStartTime());
  map.insert("End", getEndTime());
  map.insert("Runs", getRuns());
  map.insert("Groups", m_presenter->getChosenGroups());
  map.insert("Periods", m_presenter->getChosenPeriods());
  return map;
}

/**
 * Sets user input in the form of a QVariant
 *
 * This is implemented as the "standard" way of setting input in a
 * MantidWidget. In practice it is probably easier to set the input
 * using other methods.
 *
 * This function doesn't support setting runs, chosen groups or chosen periods
 * (done through UI only).
 *
 * The input QVariant is a QVariantMap of (parameter, value) pairs.
 * @param value :: [input] QVariant containing a QVariantMap
 */
void MuonFitDataView::setUserInput(const QVariant &value) {
  if (value.canConvert(QVariant::Map)) {
    const auto map = value.toMap();
    if (map.contains("Workspace index")) {
      setWorkspaceIndex(map.value("Workspace index").toUInt());
    }
    if (map.contains("Start")) {
      setStartTime(map.value("Start").toDouble());
    }
    if (map.contains("End")) {
      setEndTime(map.value("End").toDouble());
    }
  }
}

} // namespace MantidWidgets
} // namespace MantidQt
