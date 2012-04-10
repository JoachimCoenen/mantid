#include "ScriptFileInterpreter.h"
#include "ScriptOutputDisplay.h"
#include "ScriptingEnv.h"
#include "MantidQtMantidWidgets/ScriptEditor.h"

#include <QVBoxLayout>
#include <QFileInfo>
#include <QMessageBox>
#include <QMenu>
#include <QAction>
#include <QPushButton>

/**
 * Construct a widget
 * @param parent :: The parent widget
 */
ScriptFileInterpreter::ScriptFileInterpreter(QWidget *parent)
  : QWidget(parent), m_splitter(new QSplitter(Qt::Vertical,this)),
    m_editor(new ScriptEditor(this, NULL)),
    m_messages(new ScriptOutputDisplay), m_runner()
{
  setupChildWidgets();

  setContextMenuPolicy(Qt::CustomContextMenu);
  connect(this, SIGNAL(customContextMenuRequested(const QPoint &)),
          this, SLOT(showContextMenu(const QPoint&)));
}

/// Destroy the object
ScriptFileInterpreter::~ScriptFileInterpreter()
{
}

/**
 * Make sure the widget is ready to be deleted, i.e. saved etc
 */
void ScriptFileInterpreter::prepareToClose()
{
  if( !isScriptModified() ) return;

  QMessageBox msgBox(this);
  msgBox.setModal(true);
  msgBox.setWindowTitle("MantidPlot");
  msgBox.setText(tr("The current script has been modified."));
  msgBox.setInformativeText(tr("Save changes?"));
  msgBox.addButton(QMessageBox::Save);
  QPushButton *saveAsButton = msgBox.addButton("Save As...", QMessageBox::AcceptRole);
  msgBox.addButton(QMessageBox::Discard);
  int ret = msgBox.exec();
  if( msgBox.clickedButton() == saveAsButton )
  {
    m_editor->saveAs();
  }
  else if( ret == QMessageBox::Save )
  {
    m_editor->saveToCurrentFile();
  }
  else
  {
    m_editor->setModified(false);
  }
}

/**
 * Show custom context menu event
 */
void ScriptFileInterpreter::showContextMenu(const QPoint & clickPoint)
{
  QMenu context(this);
  context.addAction("&Save", m_editor, "saveToCurrentFile");

  context.insertSeparator();
  context.addAction("&Copy", m_editor, "copy");
  context.addAction("C&ut", m_editor, "cut");
  context.addAction("P&aste", m_editor, "paste");

  context.insertSeparator();
  context.addAction("E&xecute Selection", this, "executeSelection");
  context.addAction("Execute &All", this, "executeAll");

  context.exec(this->mapToGlobal(clickPoint));
}

/**
 * Set up the widget from a given scripting environment
 * @param environ :: A pointer to the current scripting environment
 * @param identifier :: A string identifier, used mainly in error messages to identify the
 * current script
 */
void ScriptFileInterpreter::setup(const ScriptingEnv & environ, const QString & identifier)
{
  setupEditor(environ, identifier);
  createScriptRunner(environ, identifier);
  connect(m_runner.data(), SIGNAL(autoCompleteListGenerated(const QStringList &)),
          m_editor, SLOT(updateCompletionAPI(const QStringList &)));
  m_runner->execute("None");
  connectScriptRunnerSignals();
}


/**
 * @return The string containing the filename of the script
 */
QString ScriptFileInterpreter::filename() const
{
  return m_editor->fileName();
}

/**
 * Has the script been modified
 * @return True if the script has been modified
 */
bool ScriptFileInterpreter::isScriptModified() const
{
  return m_editor->isModified();
}

/// Is the script running
bool ScriptFileInterpreter::isExecuting() const
{
  return m_runner->isExecuting();
}

/// Save to the currently stored name
void ScriptFileInterpreter::saveToCurrentFile()
{
  m_editor->saveToCurrentFile();
}

/// Save to a different name
void ScriptFileInterpreter::saveAs()
{
  m_editor->saveAs();
}

/**
 * Save the current script in the editor to a file
 * @param filename :: The filename to save the script in
 */
void ScriptFileInterpreter::saveScript(const QString & filename)
{
  m_editor->saveScript(filename);
}

/**
 * Save the current output text to a file
 * @param filename :: The filename to save the script in
 */

void ScriptFileInterpreter::saveOutput(const QString & filename)
{
  m_messages->saveToFile(filename);
}

/**
 * Print script
 */
void ScriptFileInterpreter::printScript()
{
  m_editor->print();
}

/// Print the output
void ScriptFileInterpreter::printOutput()
{
  m_messages->print();
}

/// Undo
void ScriptFileInterpreter::undo()
{
  m_editor->undo();
}
/// Redo
void ScriptFileInterpreter::redo()
{
  m_editor->redo();
}

/// Copy from the editor
void ScriptFileInterpreter::copy()
{
  m_editor->copy();
}

/// Cut from the editor
void ScriptFileInterpreter::cut()
{
  m_editor->cut();
}
/// Paste into the editor
void ScriptFileInterpreter::paste()
{
  m_editor->paste();
}
/// Find in editor
void ScriptFileInterpreter::showFindReplaceDialog()
{
  m_editor->showFindReplaceDialog();
}

/**
 * Execute the whole script in the editor. This is always asynchronous
 */
void ScriptFileInterpreter::executeAll(const Script::ExecutionMode mode)
{
  executeCode(m_editor->text(), mode);
}

/**
 * Execute the current selection from the editor. This is always asynchronous
 */
void ScriptFileInterpreter::executeSelection(const Script::ExecutionMode mode)
{
  if(m_editor->hasSelectedText())
  {
    executeCode(m_editor->selectedText(), mode);
  }
  else
  {
    executeAll(mode);
  }
}

/// Zoom in on script
void ScriptFileInterpreter::zoomInOnScript()
{
  m_editor->zoomIn();
}
/// Zoom out on script
void ScriptFileInterpreter::zoomOutOnScript()
{
  m_editor->zoomOut();
}

//-----------------------------------------------------------------------------
// Private members
//-----------------------------------------------------------------------------
/**
 * Create the splitter and layout for the child widgets
 */
void ScriptFileInterpreter::setupChildWidgets()
{
  m_splitter->addWidget(m_editor);
  m_splitter->addWidget(m_messages);
  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->setContentsMargins(0,0,0,0);
  mainLayout->addWidget(m_splitter);
  setLayout(mainLayout);

  setFocusProxy(m_editor);
  m_editor->setFocus();
}

/**
 * @param environ :: A pointer to the current scripting environment
 * @param identifier :: A string identifier, used mainly in error messages to identify the
 * current script
 */
void ScriptFileInterpreter::setupEditor(const ScriptingEnv & environ, const QString & identifier)
{
  if(QFileInfo(identifier).exists())
  {
    readFileIntoEditor(identifier);
  }
  m_editor->setLexer(environ.createCodeLexer());
  m_editor->padMargin();
  m_editor->setAutoMarginResize();
  m_editor->enableAutoCompletion();
  m_editor->setCursorPosition(0,0);

  connect(m_editor, SIGNAL(textChanged()), this, SIGNAL(textChanged()));
  connect(m_editor, SIGNAL(modificationChanged(bool)), this, SIGNAL(editorModificationChanged(bool)));
  connect(m_editor, SIGNAL(undoAvailable(bool)), this, SIGNAL(editorUndoAvailable(bool)));
  connect(m_editor, SIGNAL(redoAvailable(bool)), this, SIGNAL(editorRedoAvailable(bool)));
  emit editorUndoAvailable(false);
  emit editorRedoAvailable(false);
}

/**
 * @param environ :: A pointer to the current scripting environment
 * @param identifier :: A string identifier, used mainly in error messages to identify the
 * current script
 */
void ScriptFileInterpreter::createScriptRunner(const ScriptingEnv & environ, const QString & identifier)
{
  m_runner = QSharedPointer<Script>(environ.newScript(identifier,this, Script::Interactive));
}

/**
 * Connect the required signals from the script runner to the outside world
 */
void ScriptFileInterpreter::connectScriptRunnerSignals()
{
  connect(m_runner.data(), SIGNAL(started(const QString &)), m_messages, SLOT(displayMessageWithTimestamp(const QString &)));
  connect(m_runner.data(), SIGNAL(finished(const QString &)), m_messages, SLOT(displayMessageWithTimestamp(const QString &)));
  connect(m_runner.data(), SIGNAL(print(const QString &)), m_messages, SLOT(displayMessage(const QString &)));
  connect(m_runner.data(), SIGNAL(error(const QString &,const QString &, int)), m_messages, SLOT(displayError(const QString &)));
}

/**
 * Replace the contents of the editor with the given file
 * @param filename
 * @return True if the read succeeded, false otherwise
 */
bool ScriptFileInterpreter::readFileIntoEditor(const QString & filename)
{
  m_editor->setFileName(filename);
  QFile scriptFile(filename);
  if(!scriptFile.open(QIODevice::ReadOnly|QIODevice::Text))
  {
    QMessageBox::critical(this, tr("MantidPlot - File error"),
        tr("Could not open file \"%1\" for reading.").arg(filename));
    return false;
  }
  m_editor->read(&scriptFile);
  m_editor->setModified(false);
  scriptFile.close();
  return true;
}

/**
 * Use the current Script object to execute the code asynchronously
 * @param code :: The code string to run
 */
void ScriptFileInterpreter::executeCode(const QString & code, const Script::ExecutionMode mode)
{
  if( code.isEmpty() ) return;
  if(mode == Script::Asynchronous)
  {
    m_runner->executeAsync(code);
  }
  else if(mode == Script::Serialised)
  {
    m_runner->execute(code);
  }
  else
  {
    QMessageBox::warning(this, "MantidPlot", "Unknown script execution mode");
  }
}

