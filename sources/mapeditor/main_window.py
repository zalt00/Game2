# -*- coding:Utf-8 -*-

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QListWidget, QListWidgetItem, QDialog,
                             QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
                             QTextEdit, QDockWidget, QMenu, QAction, QPlainTextEdit)
from PyQt5.QtCore import pyqtSlot, Qt, QPoint
from PyQt5.QtGui import QTextCursor
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from .resources_loader import ResourcesLoader
from PyQt5 import QtCore
import os
import sys
import re
import json
import qimage2ndarray
import yaml
from . import obj_list_handler, scene_handler, infos_panel_handler, edit_panel_handler, file_handler


dir_path = '\\'.join(__file__.split('\\')[:-1])


class Window(QMainWindow):
    def __init__(self, path=''):
        super().__init__()
        uic.loadUi('.\\qt_templates\\mapeditor_mwin.ui', self)
        self.show()

        self.showMaximized()

        self.resource_loader = ResourcesLoader('resources/')

        self._i = 0

        self.template_name = None
        self.template_data = None

        self.file_handler = None

        self.infos_panel_handler = infos_panel_handler.InfosPanelHandler(self)
        self.obj_list_handler = obj_list_handler.ObjListHandler(self)
        self.scene_handler = scene_handler.SceneHandler(self)
        self.edit_panel_handler = edit_panel_handler.EditPanelHandler(self)

        self.scene_handler.init_scene()

    def set_template(self, template):
        if os.path.exists(template):
            self.template_name = template
            with open(template) as datafile:
                data = yaml.safe_load(datafile)
            self.template_data = data

            self.edit_panel_handler.init_struct_lists(self.template_data['biome'],
                                                      self.template_data['palette'])
            self.file_handler = file_handler.FileHandler(self)
            self._init_slots()

        else:
            raise ValueError('path does not exist')

    def generate_identifier(self):
        self._i += 1
        return self._i

    def _init_slots(self):
        self.x_spinbox.valueChanged.connect(self.infos_panel_handler.apply_structure_infos_changes)
        self.y_spinbox.valueChanged.connect(self.infos_panel_handler.apply_structure_infos_changes)
        self.layer_spinbox.valueChanged.connect(self.infos_panel_handler.apply_structure_infos_changes)

        self.name_lineedit.returnPressed.connect(self.infos_panel_handler.apply_structure_infos_changes)

        self.obj_list.currentItemChanged.connect(self.obj_list_handler.change_selection_in_scene)

        for listwidget in self.edit_panel_handler.struct_lists.values():
            listwidget.itemDoubleClicked.connect(self.edit_panel_handler.add_structure_to_scene)
        self.action_delete_selected_structure.triggered.connect(self.scene_handler.delete_selected_structure)

        self.action_set_bg.triggered.connect(self.scene_handler.set_bg)

        self.action_zoom_plus.triggered.connect(self.scene_handler.zoom_plus)
        self.action_zoom_minus.triggered.connect(self.scene_handler.zoom_minus)

        self.action_open.triggered.connect(self.file_handler.open)
        self.action_save_as.triggered.connect(self.file_handler.save_as)
        self.action_save.triggered.connect(self.file_handler.save)

        self.action_new_struct.triggered.connect(self.edit_panel_handler.new_structure)
        self.action_remove_current_struct.triggered.connect(self.edit_panel_handler.remove_structure)
        self.action_edit_current_struct.triggered.connect(self.edit_panel_handler.edit_current_structure)

    @staticmethod
    def canvasx2datax(x, rect):
        return x + int(rect.width()) // 2

    @staticmethod
    def canvasy2datay(y, rect):
        return -(int(rect.bottom()) + y)

    @staticmethod
    def datax2canvasx(x, rect):
        return x - int(rect.width()) // 2

    @staticmethod
    def datay2canvasy(y, rect):
        return -y - int(rect.bottom())

    def clear_objects(self):
        for data in self.scene_handler.graphics_view_items.values():
            self.scene_handler.scene.removeItem(data[0])
        self.scene_handler.graphics_view_items.clear()
        self.scene_handler.reset_bg()

        self.scene_handler.selected_item = None

        self.obj_list_handler.refresh_obj_list()

        self.infos_panel_handler.update_structure_infos()

    def load_image(self, res, palette):
        if res.endswith('.obj'):
            qimage = QtGui.QImage()
            res_obj = self.resource_loader.load(res)
            try:
                relative_image_path = res_obj.data['image']
            except KeyError:
                return
            else:
                qimage.load(os.path.join('resources/', res_obj.directory, relative_image_path))
                qimage = qimage.scaled(res_obj.width, res_obj.height)

        else:
            res_obj = self.resource_loader.load(res)
            array = palette.build(res_obj, img_format='array')
            qimage = qimage2ndarray.array2qimage(array)
            qimage = qimage.scaled(res_obj.width * res_obj.scale, res_obj.height * res_obj.scale)

        return qimage


