# -*- coding:Utf-8 -*-

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
import glob, os


class TemplateDialog(QtWidgets.QDialog):
    def __init__(self, level_templates_base_dir, button_callback):
        super().__init__()
        uic.loadUi('.\\qt_templates\\template_dialog.ui', self)
        self.show()

        self.base_dir = level_templates_base_dir

        self.confirm_button.clicked.connect(button_callback)

        self.templates = {}

        for path in glob.glob(os.path.join(self.base_dir, '*'), recursive=True):
            path = path.replace('\\', '/')
            name = os.path.basename(path)
            name = name.replace('_template.yml', '')
            name = name.replace('_', ' ')

            self.templates[name] = path
            self.template_combobox.addItem(name)
