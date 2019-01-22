# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
#     NScD Oak Ridge National Laboratory, European Spallation Source
#     & Institut Laue - Langevin
# SPDX - License - Identifier: GPL - 3.0 +
#  This file is part of the mantidqt package
#
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
from qtpy.QtWidgets import QFileDialog, QMessageBox
from qtpy.QtGui import QIcon  # noqa

from mantid.api import AnalysisDataService, AnalysisDataServiceObserver
from mantidqt.io import open_a_file_dialog
from mantidqt.project.projectloader import ProjectLoader
from mantidqt.project.projectsaver import ProjectSaver


class Project(AnalysisDataServiceObserver):
    def __init__(self, globalfiguremanager_instance):
        super(Project, self).__init__()
        # Has the project been saved, to Access this call .saved
        self.__saved = True

        # Last save locations
        self.last_project_location = None

        self.observeAll(True)

        self.project_file_ext = ".mtdproj"

        self.plot_gfm = globalfiguremanager_instance
        self.plot_gfm.add_observer(self)

    def __get_saved(self):
        return self.__saved

    saved = property(__get_saved)

    def save(self):
        """
        The function that is called if the save button is clicked on the mainwindow
        :return: None; if the user cancels
        """
        if self.last_project_location is None:
            return self.save_as()
        else:
            # Offer an are you sure? overwriting GUI
            answer = self._offer_overwriting_gui()

            if answer == QMessageBox.Yes:
                # Actually save
                self._save()
            # Else do nothing

    def save_as(self):
        """
        The function that is called if the save as... button is clicked on the mainwindow
        :return: None; if the user cancels.
        """
        path = self._save_file_dialog()
        if path is None:
            # Cancel close dialogs
            return

        overwriting = False
        # If the selected path is a project directory ask if overwrite is required?
        if os.path.exists(os.path.join(path, (os.path.basename(path) + self.project_file_ext))):
            answer = self._offer_overwriting_gui()
            if answer == QMessageBox.No:
                return
            elif answer == QMessageBox.Yes:
                overwriting = True

        if not overwriting and os.path.exists(path) and os.listdir(path) != []:
            QMessageBox.warning(None, "Empty directory or project required!",
                                "Please choose either an new directory or an already saved project", QMessageBox.Ok)
            return

        # todo: get a list of workspaces but to be implemented on GUI implementation
        self.last_project_location = path
        self._save()

    @staticmethod
    def _offer_overwriting_gui():
        """
        Offers up a overwriting QMessageBox giving the option to overwrite a project, and returns the reply.
        :return: QMessaageBox.Yes or QMessageBox.No; The value is the value selected by the user.
        """
        return QMessageBox.question(None, "Overwrite project?",
                                    "Would you like to overwrite the selected project?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    @staticmethod
    def _save_file_dialog():
        return open_a_file_dialog(accept_mode=QFileDialog.AcceptSave, file_mode=QFileDialog.Directory)

    def _save(self):
        workspaces_to_save = AnalysisDataService.getObjectNames()
        plots_to_save = self.plot_gfm.figs
        project_saver = ProjectSaver(self.project_file_ext)
        project_saver.save_project(directory=self.last_project_location, workspace_to_save=workspaces_to_save,
                                   plots_to_save=plots_to_save)
        self.__saved = True

    def load(self):
        """
        The event that is called when open project is clicked on the main window
        :return: None; if the user cancelled.
        """
        file_name = self._load_file_dialog()
        if file_name is None:
            # Cancel close dialogs
            return

        # Sanity check
        _, file_ext = os.path.splitext(file_name)

        if file_ext != ".mtdproj":
            QMessageBox.warning(None, "Wrong file type!", "Please select a valid project file", QMessageBox.Ok)

        directory = os.path.dirname(file_name)

        project_loader = ProjectLoader(self.project_file_ext)
        project_loader.load_project(directory)
        self.last_project_location = directory
        self.__saved = True

    def _load_file_dialog(self):
        return open_a_file_dialog(accept_mode=QFileDialog.AcceptOpen, file_mode=QFileDialog.ExistingFile,
                                  file_filter="Project files ( *" + self.project_file_ext + ")")

    def offer_save(self, parent):
        """
        :param parent: QWidget; Parent of the QMessageBox that is popped up
        :return: Bool; Returns false if no save needed/save complete. Returns True if need to cancel closing. However
                        will return None if self.__saved is false
        """
        # If the current project is saved then return and don't do anything
        if self.__saved:
            return

        result = self._offer_save_message_box(parent)

        if result == QMessageBox.Yes:
            self.save()
        elif result == QMessageBox.Cancel:
            return True
        # if yes or no return false
        return False

    @staticmethod
    def _offer_save_message_box(parent):
        return QMessageBox.question(parent, 'Unsaved Project', "The project is currently unsaved would you like to "
                                    "save before closing?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                    QMessageBox.Yes)

    def modified_project(self):
        self.__saved = False

    def anyChangeHandle(self):
        """
        The method that will be triggered if any of the changes in the ADS have occurred, that are checked for using the
        AnalysisDataServiceObserver class' observeAll method
        """
        self.modified_project()

    def notify(self, *args):
        """
        The method that will trigger when a plot is added, destroyed, or changed in the global figure manager.
        """
        self.modified_project()
