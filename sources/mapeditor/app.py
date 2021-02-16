# -*- coding:Utf-8 -*-

from .main_window import Window
from .template_dialog import TemplateDialog
from .config import config


class App:
    def __init__(self, path=''):
        self.window = Window()
        self.template_dialog = TemplateDialog(config['map_editor_templates_dir'], self.button_callback)
        self.template_dialog.rejected.connect(self.reject)

    def reject(self, *_, **__):
        self.window.close()

    def button_callback(self):
        template_path = self.template_dialog.templates[str(self.template_dialog.template_combobox.currentText())]
        self.template_dialog.accept()
        self.window.set_template(template_path)
