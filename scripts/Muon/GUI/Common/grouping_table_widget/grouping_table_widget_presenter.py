from __future__ import (absolute_import, division, print_function)

import re

from Muon.GUI.Common.utilities import run_string_utils as run_utils
from Muon.GUI.Common.muon_group import MuonGroup

maximum_number_of_groups = 20


class GroupingTablePresenter(object):

    def __init__(self, view, model):
        self._view = view
        self._model = model

        self._view.on_add_group_button_clicked(self.handle_add_group_button_clicked)
        self._view.on_remove_group_button_clicked(self.handle_remove_group_button_clicked)

        self._view.on_user_changes_group_name(self.validate_group_name)
        self._view.on_user_changes_detector_IDs(self.validate_detector_ids)

        self._view.on_table_data_changed(self.handle_data_change)

        self._dataChangedNotifier = lambda: 0

    def show(self):
        self._view.show()

    def on_data_changed(self, notifier):
        self._dataChangedNotifier = notifier

    def notify_data_changed(self):
        self._dataChangedNotifier()

    def _is_edited_name_duplicated(self, new_name):
        is_name_column_being_edited = self._view.grouping_table.currentColumn() == 0
        is_name_unique = True
        if new_name in self._model.group_and_pair_names:
            is_name_unique = False
        return is_name_column_being_edited and not is_name_unique

    def validate_group_name(self, text):
        if self._is_edited_name_duplicated(text):
            self._view.warning_popup("Groups and pairs must have unique names")
            return False
        if not re.match(run_utils.valid_name_regex, text):
            self._view.warning_popup("Group names should only contain digits, characters and _")
            return False
        return True

    def validate_detector_ids(self, text):
        if re.match(run_utils.run_string_regex, text):
            return True
        self._view.warning_popup("Invalid detector list.")
        return False

    def disable_editing(self):
        self._view.disable_editing()

    def enable_editing(self):
        self._view.enable_editing()

    def add_group(self, group):
        """Adds a group to the model and view"""
        if self._view.num_rows() >= maximum_number_of_groups:
            self._view.warning_popup("Cannot add more than {} groups.".format(maximum_number_of_groups))
            return
        self.add_group_to_view(group)
        self.add_group_to_model(group)
        self._view.notify_data_changed()
        self.notify_data_changed()

    def add_group_to_model(self, group):
        self._model.add_group(group)

    def add_group_to_view(self, group):
        self._view.disable_updates()
        assert isinstance(group, MuonGroup)
        entry = [str(group.name), run_utils.run_list_to_string(group.detectors), str(group.n_detectors)]
        self._view.add_entry_to_table(entry)
        self._view.enable_updates()

    def handle_add_group_button_clicked(self):
        group = self._model.construct_empty_group(self._view.num_rows() + 1)
        self.add_group(group)

    def handle_remove_group_button_clicked(self):
        group_names = self._view.get_selected_group_names()
        if not group_names:
            self.remove_last_row_in_view_and_model()
        else:
            self.remove_selected_rows_in_view_and_model(group_names)
        self._view.notify_data_changed()
        self.notify_data_changed()

    def remove_selected_rows_in_view_and_model(self, group_names):
        self._view.remove_selected_groups()
        self._model.remove_groups_by_name(group_names)

    def remove_last_row_in_view_and_model(self):
        if self._view.num_rows() > 0:
            name = self._view.get_table_contents()[-1][0]
            self._view.remove_last_row()
            self._model.remove_groups_by_name([name])

    def handle_data_change(self, row, col):
        changed_item = self._view.get_table_item_text(row, col)
        update_model = True
        if col == 0 and not self.validate_group_name(changed_item):
            update_model = False
        if col == 1 and not self.validate_detector_ids(changed_item):
            update_model = False
        if update_model:
            self.update_model_from_view()

        self.update_view_from_model()
        self._view.notify_data_changed()
        self.notify_data_changed()

    def update_model_from_view(self):
        table = self._view.get_table_contents()
        self._model.clear_groups()
        for entry in table:
            detector_list = run_utils.run_string_to_list(str(entry[1]))
            group = MuonGroup(group_name=str(entry[0]), detector_ids=detector_list)
            self._model.add_group(group)

    def update_view_from_model(self):
        self._view.disable_updates()

        self._view.clear()
        for name, group in self._model.groups.items():
            self.add_group_to_view(group)

        self._view.enable_updates()
