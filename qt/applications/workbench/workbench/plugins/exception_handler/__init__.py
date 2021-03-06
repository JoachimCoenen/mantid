# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI,
#     NScD Oak Ridge National Laboratory, European Spallation Source
#     & Institut Laue - Langevin
# SPDX - License - Identifier: GPL - 3.0 +
#  This file is part of the mantid workbench.
from __future__ import absolute_import

import traceback

from ErrorReporter.error_report_presenter import ErrorReporterPresenter
from ErrorReporter.errorreport import CrashReportPage
from mantid import UsageService
from mantid.kernel import logger
from workbench.plugins.exception_handler.error_messagebox import WorkbenchErrorMessageBox


def exception_logger(main_window, exc_type, exc_value, exc_traceback):
    """
    Captures ALL EXCEPTIONS.
    Prevents the Workbench from crashing silently, instead it logs the error on ERROR level.

    :param main_window: A reference to the main window, that will be used to close it in case of the user
                        choosing to terminate the execution.
    :param exc_type: The type of the exception
    :param exc_value: Value of the exception, typically contains the error message.
    :param exc_traceback: Stack trace of the exception.
    """
    logger.error("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    if UsageService.isEnabled():
        page = CrashReportPage(show_continue_terminate=True)
        presenter = ErrorReporterPresenter(page, '', 'workbench')
        presenter.show_view_blocking()
        if not page.continue_working:
            main_window.close()
    else:
        # show the exception message without the traceback
        WorkbenchErrorMessageBox(main_window, "".join(traceback.format_exception_only(exc_type, exc_value))).exec_()
