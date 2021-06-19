# -*- coding:Utf-8 -*-

from PyQt5 import QtWidgets, uic
from .config import config
import os


class ConstraintFrame(QtWidgets.QWidget):
    def __init__(self, objects, name='', anchor_a=(0, 0), anchor_b=(0, 0), resource='special_objects/rope.obj',
                 object_a='', object_b=''):
        super().__init__()
        uic.loadUi(os.path.normpath(
            os.path.join(config['qt_templates_dir'], 'constraint_widget.ui')), self)

        self.name = name
        self.anchor_a = list(anchor_a)
        self.anchor_b = list(anchor_b)
        self.resource = resource
        self.object_a = object_a
        self.object_b = object_b

        self.objects = objects
        self.name_to_id = {}

        self.init_combobox(self.object_a_combobox)
        self.init_combobox(self.object_b_combobox)

        self.remove_callback = lambda: None
        self.display_callback = lambda *_, **__: None

        self.scene_line = None

        self.remove_button.clicked.connect(self.remove)

        self.display_checkbox.toggled.connect(self.display)

    def remove(self):
        self.remove_callback()

    def display(self, value):
        self.display_callback(value, self)

    def update_widget(self):
        self.object_a_combobox.setCurrentText(self.object_a)
        self.object_b_combobox.setCurrentText(self.object_b)

        self.name_lineedit.setText(self.name)

        self.anchor_a_x_spinbox.setValue(self.anchor_a[0])
        self.anchor_a_y_spinbox.setValue(self.anchor_a[1])
        self.anchor_b_x_spinbox.setValue(self.anchor_b[0])
        self.anchor_b_y_spinbox.setValue(self.anchor_b[1])

        self.res_lineedit.setText(self.resource)

    def update_data(self):

        self.object_a = self.object_a_combobox.currentText()
        self.object_b = self.object_b_combobox.currentText()

        self.name = self.name_lineedit.text()

        self.anchor_a[0] = self.anchor_a_x_spinbox.value()
        self.anchor_a[1] = self.anchor_a_y_spinbox.value()
        self.anchor_b[0] = self.anchor_b_x_spinbox.value()
        self.anchor_b[1] = self.anchor_b_y_spinbox.value()

        self.resource = self.res_lineedit.text()

        if self.display_checkbox.isChecked():
            self.display(False)
            self.display(True)

    def reinit_all_comboboxes(self):
        self.reinit_combobox(self.object_a_combobox)
        self.reinit_combobox(self.object_b_combobox)
        self.update_widget()

    def reinit_combobox(self, combobox):
        combobox.clear()
        self.name_to_id.clear()
        self.init_combobox(combobox)

    def init_combobox(self, combobox):
        for id_, data in self.objects.items():
            name = data[3]
            self.name_to_id[name] = id_
            combobox.addItem(name)


