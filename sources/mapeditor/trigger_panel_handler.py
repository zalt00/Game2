# -*- coding:Utf-8 -*-


from . import trigger_panel_widgets as widgets
from .config import config
import yaml
from PyQt5 import QtWidgets


class TriggerPanelHandler:
    def __init__(self, window):
        self.window = window

        with open(config['trigger_actions_templates_path']) as datafile:
            self.trigger_actions_templates = yaml.safe_load(datafile)

        for action_name in self.trigger_actions_templates.keys():
            self.window.addable_actions_combobox.addItem(action_name)

        self._triggers = []  # list[] -> [name, dict[property_name] -> property_value]
        #  - id: int
        #  - enabled: bool
        #  - actions: list[] -> [action_name: str, action_data: (dict[str] -> Any)]
        #  - left: Union[NoneType, int]       \
        #  - right: Union[NoneType, int]       |
        #  - top: Union[NoneType, int]         | describe the trigger's bounding box
        #  - bottom: Union[NoneType, int]     /

        self._selected_trigger = None  # index of the trigger in the self._triggers list or None

        self._action_widgets = []

        self.currently_displayed_bbox = ()

        self.empty_actions_scroll_area_content_layout()

    def add_trigger(self):
        id_ = self.window.generate_identifier()

        name = f'trigger{id_}'

        self.window.triggers_listwidget.addItem(name)

        # default values for the properties of the trigger
        self._triggers.append([name, dict(enabled=True, id=id_, actions=list(), left=None,
                                          right=None, bottom=None, top=None)])

    def select_trigger(self, index):
        self.window.edit_trigger_groupbox.setEnabled(True)
        self._selected_trigger = index
        self.refresh_edit_trigger_box()

    def refresh_edit_trigger_box(self):
        if self._selected_trigger is not None:
            self.empty_actions_scroll_area_content_layout()
            trigger_name, trigger_data = self._triggers[self._selected_trigger]

            self.window.trigger_name_lineedit.setText(trigger_name)

            for side in ('left', 'right', 'top', 'bottom'):
                checkbox_attr_name = f'trigger_{side}_checkbox'
                if trigger_data[side] is None:
                    getattr(self.window, checkbox_attr_name).setChecked(False)
                else:
                    getattr(self.window, checkbox_attr_name).setChecked(True)

                    spinbox_attr_name = f'trigger_{side}_spinbox'
                    getattr(self.window, spinbox_attr_name).setValue(trigger_data[side])

            self.window.trigger_id_spinbox.setValue(trigger_data['id'])
            self.window.trigger_enabled_checkbox.setChecked(trigger_data['enabled'])

            for action_name, parameters in trigger_data['actions']:
                action_data = self.trigger_actions_templates[action_name]
                widget = self._create_action_widget(action_name, action_data)
                widget.set_parameters(parameters)

    def save_trigger(self):
        if self._selected_trigger is not None:
            _, trigger_data = self._triggers[self._selected_trigger]

            name = self.window.trigger_name_lineedit.text()
            self._triggers[self._selected_trigger][0] = name
            self.window.triggers_listwidget.item(self._selected_trigger).setText(name)

            for side in ('left', 'right', 'top', 'bottom'):
                spinbox_attr_name = f'trigger_{side}_spinbox'
                spinbox = getattr(self.window, spinbox_attr_name)
                if spinbox.isEnabled():
                    trigger_data[side] = spinbox.value()
                else:
                    trigger_data[side] = None

            new_id = self.window.trigger_id_spinbox.value()
            for _, _data in self._triggers:
                if new_id == _data['id']:
                    new_id = trigger_data['id']
            trigger_data['id'] = new_id

            trigger_data['enabled'] = self.window.trigger_enabled_checkbox.isChecked()

            trigger_data['actions'] = list()
            for action_widget in self._action_widgets:
                try:
                    parameters = action_widget.get_parameters()
                except AssertionError:
                    pass
                else:
                    trigger_data['actions'].append([action_widget.action_name, parameters])

            self.refresh_edit_trigger_box()

    def display_trigger(self, display=True):
        if self._selected_trigger is not None:
            if display:
                left = self._triggers[self._selected_trigger][1]['left']
                right = self._triggers[self._selected_trigger][1]['right']
                top = self._triggers[self._selected_trigger][1]['top']
                bottom = self._triggers[self._selected_trigger][1]['bottom']

                if left is None:
                    left = -2000
                if right is None:
                    right = 20000
                if top is None:
                    top = 5000
                if bottom is None:
                    bottom = -5000

                self.currently_displayed_bbox = self.window.scene_handler.display_trigger_bbox(
                    left, right, -top, -bottom)
            else:
                self.window.scene_handler.remove_trigger_bbox(self.currently_displayed_bbox)

    def add_action(self):
        if self._selected_trigger is not None:
            action_name = self.window.addable_actions_combobox.currentText()
            action_data = self.trigger_actions_templates[action_name]
            self._create_action_widget(action_name, action_data)

    def _create_action_widget(self, action_name, action_data):
        widget = widgets.TriggerActionWidget(action_name, action_data)
        self.window.trigger_actions_scroll_area_content.layout().addWidget(widget)
        self._action_widgets.append(widget)
        return widget

    def empty_actions_scroll_area_content_layout(self):
        self._action_widgets.clear()
        layout = self.window.trigger_actions_scroll_area_content.layout()
        is_there_a_spacer = False
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if isinstance(item, QtWidgets.QSpacerItem):
                is_there_a_spacer = True
            else:
                widget_to_remove = layout.itemAt(i).widget()
                # remove it from the layout list
                layout.removeWidget(widget_to_remove)
                # remove it from the gui
                widget_to_remove.setParent(None)
                widget_to_remove.deleteLater()

        if not is_there_a_spacer:
            spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            layout.addItem(spacer)



