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
import dataclasses
import glob

dir_path = '\\'.join(__file__.split('\\')[:-1])


@dataclasses.dataclass
class ItemData:
    res: str
    qimage: QtGui.QImage


class Window(QMainWindow):
    def __init__(self, path=''):
        super().__init__()
        uic.loadUi('.\\qt_templates\\mapeditor_mwin.ui', self)
        self.show()

        self.showMaximized()

        self._resource_loader = ResourcesLoader('resources/')
        self._palette = None
        self._struct_lists = {}
        self._scene = None

        self._preview_scene = QtWidgets.QGraphicsScene()
        self.preview_graphics_view.setScene(self._preview_scene)

        self._item_to_data = {}

        self._list_item_to_id = {}

        self._i = 0

        self._graphics_view_items = {}

        self._selected_item = None

        self._bg = None

        self._updating_structure_infos = False

        self._init_struct_lists('forest', 'structure_palettes/forest/forest_structure_tilesets.stsp')
        self._init_scene()
        self._init_slots()

    def _init_struct_lists(self, biome, palette):
        self._palette = self._resource_loader.load(palette)

        self._struct_lists = dict(
            mainbuilds=self.mb_struct_list,
            background_decorations=self.bgd_struct_list,
            dynamic_structures=self.ds_struct_list,
            spikes=self.sk_struct_list,
            decorations=self.dec_struct_list,
            foreground_decorations=self.fgd_struct_list,
            special_objects=self.so_struct_list
        )

        for struct_list in self._struct_lists.values():
            struct_list.setViewMode(QtWidgets.QListView.IconMode)

        main_structures = 'mainbuilds', 'background_decorations', 'dynamic_structures', 'spikes'
        for struct_type in main_structures:
            for path in glob.glob(f'resources/structures/{struct_type}/{biome}/*.st', recursive=True):
                res_name = path.replace('\\', '/').replace('resources/', '')
                self._add_structure(res_name, self._struct_lists[struct_type])

            for path in glob.glob(f'resources/structures/{struct_type}/{biome}/*.obj', recursive=True):
                res_name = path.replace('\\', '/').replace('resources/', '')
                self._add_structure(res_name, self._struct_lists[struct_type])

        others = 'foreground_decorations', 'decorations'
        for struct_type in others:

            for path in glob.glob(f'resources/{struct_type}/{biome}/*.obj'):
                res_name = path.replace('\\', '/').replace('resources/', '')
                self._add_structure(res_name, self._struct_lists[struct_type])

            for path in glob.glob(f'resources/{struct_type}/{biome}/*.st'):
                res_name = path.replace('\\', '/').replace('resources/', '')
                self._add_structure(res_name, self._struct_lists[struct_type])

        for path in glob.glob(f'resources/special_objects/*.obj'):
            res_name = path.replace('\\', '/').replace('resources/', '')
            self._add_structure(res_name, self._struct_lists['special_objects'])

    def _add_structure(self, res, struct_list):
        if res.endswith('.obj'):
            qimage = QtGui.QImage()
            res_obj = self._resource_loader.load(res)
            try:
                relative_image_path = res_obj.data['image']
            except KeyError:
                return
            else:
                qimage.load(os.path.join('resources/', res_obj.directory, relative_image_path))
                qimage = qimage.scaled(res_obj.width, res_obj.height)

        else:

            res_obj = self._resource_loader.load(res)
            array = self._palette.build(res_obj, img_format='array')
            qimage = qimage2ndarray.array2qimage(array)
            qimage = qimage.scaled(res_obj.width * res_obj.scale, res_obj.height * res_obj.scale)

        item_data = ItemData(res, qimage)

        item = QtWidgets.QListWidgetItem()
        icon = QtGui.QIcon()

        pixmap = QtGui.QPixmap(qimage)
        icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon)
        struct_list.addItem(item)

        self._item_to_data[id(item)] = item_data

    def _init_scene(self):
        self._scene = QtWidgets.QGraphicsScene()
        self.graphics_view.setScene(self._scene)

        self._scene.addLine(0, 0, 10000, 0, QtGui.QPen(QtGui.QColor(0x21A6FF))).setZValue(30)
        self._scene.addLine(0, -720, 10000, -720, QtGui.QPen(QtGui.QColor(0x21A6FF))).setZValue(30)
        self._scene.addLine(0, 0, 0, -720, QtGui.QPen(QtGui.QColor(0x21A6FF))).setZValue(30)

        self.graphics_view.setSceneRect(-300, -1900, 10000, 2000)

    def _init_item(self, qimage, res):
        self._i += 1
        item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(qimage))
        self._scene.addItem(item)
        pos = self.graphics_view.mapToScene(600, 300)
        item.setX(pos.x())
        item.setY(pos.y())

        item.setAcceptedMouseButtons(Qt.LeftButton)
        item.setCursor(Qt.OpenHandCursor)
        item.setFlags(item.ItemIsMovable | item.ItemIsSelectable)
        item.mousePressEvent = self._get_item_mousepress_callback(self._i)
        item.mouseMoveEvent = self._get_item_mousemove_callback(item)

        list_item = QtWidgets.QListWidgetItem('struct' + str(self._i))
        self.obj_list.addItem(list_item)

        self._graphics_view_items[self._i] = [item, res, qimage, 'struct' + str(self._i), 0, list_item]

        self._list_item_to_id[id(list_item)] = self._i

    def _get_item_mousepress_callback(self, id_):
        def callback(_):
            self._scene.clearSelection()
            if self._selected_item is not None:
                self._graphics_view_items[self._selected_item][5].setSelected(False)
            self._selected_item = id_
            self._graphics_view_items[self._selected_item][5].setSelected(True)

            self._update_structure_infos()
        return callback

    def _get_item_mousemove_callback(self, item):
        mouse_move = item.mouseMoveEvent

        def callback(event):
            x, y = None, None
            if event.modifiers() & Qt.ShiftModifier:
                y = item.y()
            if event.modifiers() & Qt.ControlModifier:
                x = item.x()

            self._update_structure_infos()
            to_rtn = mouse_move(event)

            if x is not None:
                item.setX(x)
            if y is not None:
                item.setY(y)

            return to_rtn

        return callback

    def _update_structure_infos(self):
        self._updating_structure_infos = True
        self._preview_scene.clear()
        if self._selected_item is not None:
            data = self._graphics_view_items[self._selected_item]

            self._preview_scene.addPixmap(QtGui.QPixmap(data[2]))

            self.resource_label.setText(data[1])

            self.name_lineedit.setText(data[3])

            self.layer_spinbox.setValue(data[4])

            rect = data[0].boundingRect()
            x, y = int(data[0].x()), int(data[0].y())

            self.x_spinbox.setValue(x + int(rect.width()) // 2)
            bottom = -(int(rect.bottom()) + y)
            self.y_spinbox.setValue(bottom)

            left = int(rect.left()) + x
            right = int(rect.right()) + x
            top = -(int(rect.top()) + y)
            self.bbox_label.setText(f'{left}, {bottom}, {right}, {top}')
        self._updating_structure_infos = False

    def _init_slots(self):
        self.x_spinbox.valueChanged.connect(self._apply_structure_infos_changes)
        self.y_spinbox.valueChanged.connect(self._apply_structure_infos_changes)
        self.layer_spinbox.valueChanged.connect(self._apply_structure_infos_changes)

        self.name_lineedit.returnPressed.connect(self._apply_structure_infos_changes)

        self.obj_list.currentItemChanged.connect(self._change_selection_in_scene)

        for listwidget in self._struct_lists.values():
            listwidget.itemDoubleClicked.connect(self._add_structure_to_scene)
        self.action_delete_selected_structure.triggered.connect(self._delete_selected_structure)

        self.action_set_bg.triggered.connect(self._set_bg)

        self.action_zoom_plus.triggered.connect(self._zoom_plus)
        self.action_zoom_minus.triggered.connect(self._zoom_minus)

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

    def _apply_structure_infos_changes(self, *_, **__):
        if not self._updating_structure_infos:
            if self._selected_item is not None:
                data = self._graphics_view_items.get(self._selected_item, None)
                if data is not None:
                    data[3] = self.name_lineedit.text()
                    data[4] = self.layer_spinbox.value()
                    data[0].setZValue(data[4])

                    rect = data[0].boundingRect()
                    data[0].setX(self.datax2canvasx(self.x_spinbox.value(), rect))
                    data[0].setY(self.datay2canvasy(self.y_spinbox.value(), rect))

                    self._update_structure_infos()

    def _change_selection_in_scene(self, current, previous):
        try:
            id_ = self._list_item_to_id[id(current)]
        except KeyError:
            pass
        else:
            self._graphics_view_items[id_][0].setSelected(True)
            if self._selected_item is not None:
                self._graphics_view_items[self._selected_item][0].setSelected(False)
            self._selected_item = id_
            self._update_structure_infos()

    def _add_structure_to_scene(self, item):
        data = self._item_to_data[id(item)]
        self._init_item(data.qimage, data.res)

    def _delete_selected_structure(self):
        if self._selected_item is not None:
            data = self._graphics_view_items[self._selected_item]

            i = self._selected_item
            self._selected_item = None

            self._scene.removeItem(data[0])
            self._graphics_view_items.pop(i)
            self._refresh_obj_list()

            self._update_structure_infos()

    def _refresh_obj_list(self):
        self.obj_list.clear()
        self._list_item_to_id.clear()
        for i, data in self._graphics_view_items.items():
            list_item = QtWidgets.QListWidgetItem(data[3])
            self.obj_list.addItem(list_item)

            self._graphics_view_items[i][5] = list_item

            self._list_item_to_id[id(list_item)] = i

    def _set_bg(self):

        path, _ = QFileDialog.getOpenFileName(self, 'Ouvrir', 'resources/backgrounds',
                                              "Image (*.png);;Tous les fichiers (*)")
        if path:
            if self._bg is not None:
                self._scene.removeItem(self._bg[0])

            qimage = QtGui.QImage()
            qimage.load(path)

            item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(qimage))
            item.setZValue(-50)
            self._scene.addItem(item)
            item.setY(-100 - 720)

            item.setAcceptedMouseButtons(Qt.MouseButton(0))
            self._bg = item

    def _zoom_plus(self):
        self.graphics_view.scale(1.25, 1.25)

    def _zoom_minus(self):
        self.graphics_view.scale(0.8, 0.8)



