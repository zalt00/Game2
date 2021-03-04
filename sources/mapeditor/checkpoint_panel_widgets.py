# -*- coding:Utf-8 -*-

from PyQt5 import QtWidgets, uic
from .config import config
import os


class Checkpoint(QtWidgets.QWidget):
    def __init__(self, id_, remove_callback, default_x=0, default_y=0):
        super().__init__()
        uic.loadUi(os.path.normpath(
            os.path.join(config['qt_templates_dir'], 'checkpoint_widget.ui')), self)

        self.id_ = id_
        self.x = default_x
        self.y = default_y

        self.update_widget()

        self.remove_callback = remove_callback
        self.remove_button.clicked.connect(self.remove)

    def remove(self):
        self.remove_callback()

    def update_widget(self):
        self.id_label.setText(f'Id= {self.id_}')
        self.x_spinbox.setValue(int(self.x))
        self.y_spinbox.setValue(int(self.y))

    def update_data(self):
        self.x = self.x_spinbox.value()
        self.y = self.y_spinbox.value()

