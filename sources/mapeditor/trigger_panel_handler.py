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

        self.action_type_to_action_name = dict()
        for action_name, action_parameters in self.trigger_actions_templates.items():
            self.action_type_to_action_name[action_parameters['type_']] = action_name

        for action_name in self.trigger_actions_templates.keys():
            self.window.addable_actions_combobox.addItem(action_name)

        self._triggers = []  # list[] -> [name, dict[property_name] -> property_value]

        # trigger properties:
        #  - id: int
        #  - enabled: bool
        #  - actions: list[] -> [action_name: str, action_data: (dict[str] -> Any)]
        #  - left: Union[NoneType, int]       \
        #  - right: Union[NoneType, int]       |
        #  - top: Union[NoneType, int]         | describe the trigger's bounding box
        #  - bottom: Union[NoneType, int]     /

        self._selected_trigger = None  # index of the trigger in the self._triggers list or None if no trigger is
        # selected

        self._action_widgets = []

        self.currently_displayed_bbox = ()

        self.empty_actions_scroll_area_content_layout()

    def add_trigger(self):
        id_ = self.window.generate_identifier()
        while id_ in set(_d['id'] for (_, _d) in self._triggers):
            id_ += 1

        name = f'trigger{id_}'

        # default values for the properties of the trigger
        self._init_trigger(name, dict(enabled=True, id=id_, actions=list(), left=None,
                                      right=None, bottom=None, top=None))

    def _init_trigger(self, name, properties):
        self.window.triggers_listwidget.addItem(name)

        self._triggers.append([name, properties])

    def init_triggers_data(self, triggers_data):
        self.clear_triggers()
        for trigger_name, trigger_properties in triggers_data.items():
            actions = []
            for action_parameters in trigger_properties['actions']:
                action_name = self.action_type_to_action_name[action_parameters['type_']]
                actions.append([action_name, action_parameters])
            trigger_properties['actions'] = actions

            for property_name in ('left', 'right', 'top', 'bottom'):
                if property_name not in trigger_properties:
                    trigger_properties[property_name] = None
            self._init_trigger(trigger_name, trigger_properties)

    def clear_triggers(self):
        self.window.edit_trigger_groupbox.setEnabled(False)
        self._selected_trigger = None
        self.window.triggers_listwidget.clear()
        self._triggers.clear()

    def select_trigger(self, index):
        if index != -1 and index < len(self._triggers):
            self.window.edit_trigger_groupbox.setEnabled(True)
            self._selected_trigger = index
            self.refresh_edit_trigger_box()
        else:
            self._selected_trigger = None
            self.window.edit_trigger_groupbox.setEnabled(False)

    def refresh_edit_trigger_box(self):
        if self._selected_trigger is not None:

            if self.window.display_trigger_button.isChecked():
                self.display_trigger(False)
                self.display_trigger(True)

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

            while new_id in set(_d['id'] for (_name, _d) in self._triggers if _name != name):
                new_id += 1

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

    def remove_trigger(self):
        if self._selected_trigger is not None:
            id_to_remove = self._selected_trigger
            self._selected_trigger = None
            self._triggers.pop(id_to_remove)
            self.window.triggers_listwidget.takeItem(id_to_remove)
            self.window.edit_trigger_groupbox.setEnabled(False)

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

    def get_triggers_data(self):
        output_data = dict()
        for trigger_name, trigger_properties in self._triggers:
            trigger_data = dict()
            output_data[trigger_name] = trigger_data
            for property_name, property_value in trigger_properties.items():
                if property_name in ('left', 'right', 'top', 'bottom'):
                    if property_value is not None:
                        trigger_data[property_name] = property_value
                elif property_name == 'actions':
                    actions = []
                    for _, action_data in property_value:
                        actions.append(action_data)
                    trigger_data[property_name] = actions
                else:
                    trigger_data[property_name] = property_value

        return output_data

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



