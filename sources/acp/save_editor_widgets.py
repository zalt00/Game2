# -*- coding:Utf-8 -*-


from PyQt5 import uic
from PyQt5 import QtWidgets
from utils.save_modifier import SaveComponent


class SaveComponentGroup(QtWidgets.QWidget):
    def __init__(self, text):
        super().__init__()
        uic.loadUi('.\\qt_templates\\acp_save_component_grouping_widget.ui', self)
        self.group_box.setTitle(text)

        self.widgets = []

    def add_widget(self, w):
        self.group_box.layout().addWidget(w)
        self.widgets.append(w)

    def remove_widget(self, w):
        self.widgets.remove(w)


class SaveComponentWidget(QtWidgets.QWidget):
    def __init__(self, label, dtype, save_component_id, save_id):
        super().__init__()
        uic.loadUi('.\\qt_templates\\acp_save_component_widget.ui', self)

        self.label.setText(str(save_component_id))

        self.save = SaveComponent(save_component_id)
        self.save_id = save_id

        self.label_lineedit.setText(label)

        self._data_type = 'integer'

        self.dtype2frame = dict(
            booleans=self.checkboxes_frame,
            shorts=self.double_spinbox_frame,
            integer=self.spinbox_frame
        )

        self.checkboxes_frame.setHidden(True)
        self.double_spinbox_frame.setHidden(True)
        self.spinbox_frame.setHidden(True)

        self.type_combobox.currentTextChanged.connect(self._set_data_type)

        self.data_type = dtype

    def _set_data_type(self, value):
        self.data_type = str(value)

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        assert value in {'integer', 'shorts', 'booleans'}

        self.dtype2frame[self.data_type].setHidden(True)
        self.dtype2frame[value].setHidden(False)

        self._data_type = value
        combobox_value = self.type_combobox.currentText()
        if combobox_value != value:
            self.type_combobox.setCurrentText(value)

        self.refresh_value()

    def refresh_value(self):
        if self.data_type == 'integer':
            self.int_spinbox.setValue(self.save.get(self.save_id))

        elif self.data_type == 'shorts':
            a, b = self.save.get_bytes(self.save_id)
            self.s_spinbox_1.setValue(a)
            self.s_spinbox_2.setValue(b)

        elif self.data_type == 'booleans':
            unformated_name = 'checkBox_{}'
            booleans = self.save.get_booleans(self.save_id)
            for i, value in enumerate(booleans):
                getattr(self, unformated_name.format(i + 1)).setChecked(value)

    def apply_on_save_component(self):
        if self.data_type == 'integer':
            value = self.int_spinbox.value()
            self.save.set(value, self.save_id)

        elif self.data_type == 'shorts':
            v1 = self.s_spinbox_1.value()
            v2 = self.s_spinbox_2.value()

            self.save.set_bytes(v1, v2, self.save_id)

        elif self.data_type == 'booleans':
            booleans = []
            unformated_name = 'checkBox_{}'
            for i, value in enumerate(booleans):
                booleans.append(getattr(self, unformated_name.format(i + 1)).isChecked())

            self.save.set_booleans(booleans, self.save_id)

    def update_label(self, label_dict):
        label_dict[str(hash((self.save.i, self.save_id)))] = self.label_lineedit.text()

    def update_dtype(self, dtypes_dict):
        dtypes_dict[str(hash((self.save.i, self.save_id)))] = self.data_type







