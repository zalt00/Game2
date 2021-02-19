# -*- coding:Utf-8 -*-


from PyQt5 import QtWidgets, uic
from .config import config
import os
import yaml


class TriggerActionParameterEntry(QtWidgets.QWidget):
    def __init__(self, template_name, default_value=None):
        super().__init__()
        uic.loadUi(os.path.normpath(
            os.path.join(config['qt_templates_dir'], template_name)), self)
        if default_value is not None:
            self.line_edit.setText(str(default_value))

    def get_raw_entry_content(self):
        return self.line_edit.text()

    def set_raw_content(self, content):
        self.line_edit.setText(content)


class OptionalTriggerActionParameterEntry(TriggerActionParameterEntry):
    def __init__(self, parameter_name, default_value=None):
        super(OptionalTriggerActionParameterEntry, self).__init__('optional_trigger_action_parameter_entry.ui',
                                                                  default_value=default_value)
        self.checkbox.setText(parameter_name)

    def get_content(self):
        return self.line_edit.isEnabled(), yaml.safe_load(self.get_raw_entry_content())

    def set_content(self, content):
        self.checkbox.setChecked(True)
        self.set_raw_content(str(content))


class RequiredTriggerActionParameterEntry(TriggerActionParameterEntry):
    def __init__(self, parameter_name, default_value=None):
        super(RequiredTriggerActionParameterEntry, self).__init__('required_trigger_action_parameter_entry.ui',
                                                                  default_value=default_value)
        self.label.setText(parameter_name)

    def get_content(self):
        return True, yaml.safe_load(self.get_raw_entry_content())

    def set_content(self, content):
        self.set_raw_content(str(content))


class TriggerActionWidget(QtWidgets.QWidget):
    def __init__(self, action_name, action_data):
        super().__init__()
        uic.loadUi(os.path.normpath(
            os.path.join(config['qt_templates_dir'], 'trigger_action_widget.ui')), self)

        self.group_box.setTitle(action_name)

        self.action_name = action_name

        self._entries = dict()  # dict[parameter_name] -> [widget: QWidget, expected_data_type: str, optional: bool]
        self._action_type = ''

        for parameter_name, parameter_data in action_data.items():
            if parameter_name == 'type_':
                self._action_type = parameter_data
            else:
                self.add_parameter_entry(parameter_name, parameter_data)

    def get_parameters(self):
        parameters = dict()
        for parameter_name, (widget, expected_data_type, _) in self._entries.items():
            is_filled, value = widget.get_content()
            if is_filled:
                assert self.is_type(value, expected_data_type)
                parameters[parameter_name] = value

        parameters['type_'] = self._action_type
        return parameters

    def set_parameters(self, parameters):
        for parameter_name, parameter_value in parameters.items():
            if parameter_name != 'type_':
                self._entries[parameter_name][0].set_content(parameter_value)

    @staticmethod
    def is_type(value, data_type):
        if data_type in ('str', 'string'):
            return isinstance(value, str)
        elif data_type == 'bool':
            return isinstance(value, bool)
        elif data_type == 'list':
            return isinstance(value, list)
        elif data_type == 'int':
            return isinstance(value, int)
        elif data_type == 'float':
            return isinstance(value, (int, float))

    def _add_entry(self, widget, parameter_name, parameter_data):
        self._entries[parameter_name] = [widget, parameter_data['type'], parameter_data['optional']]
        self.group_box.layout().addWidget(widget)

    def add_optional_parameter_entry(self, parameter_name, parameter_data):
        widget = OptionalTriggerActionParameterEntry(parameter_name, default_value=parameter_data['default'])
        self._add_entry(widget, parameter_name, parameter_data)

    def add_required_parameter_entry(self, parameter_name, parameter_data):
        widget = RequiredTriggerActionParameterEntry(parameter_name, default_value=parameter_data['default'])
        self._add_entry(widget, parameter_name, parameter_data)

    def add_parameter_entry(self, parameter_name, parameter_data):
        if parameter_data['optional']:
            self.add_optional_parameter_entry(parameter_name, parameter_data)
        else:
            self.add_required_parameter_entry(parameter_name, parameter_data)

