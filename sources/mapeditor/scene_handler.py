# -*- coding:Utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
import os


class SceneHandler:
    def __init__(self, window):
        self.window = window
        self.graphics_view = self.window.graphics_view
        self._graphics_view_items = {}

        self._scene = None
        self._selected_item = None
        self._bg = None
        self._bg_res = None

    @property
    def scene(self):
        return self._scene

    @property
    def bg_res(self):
        return self._bg_res

    @property
    def selected_item(self):
        return self._selected_item

    @selected_item.setter
    def selected_item(self, value):
        if value is None:
            self._selected_item = None
        elif value in self.graphics_view_items:
            self._selected_item = value
        else:
            raise ValueError(f'item of id "{value}" does not exist')

    @property
    def graphics_view_items(self):
        return self._graphics_view_items

    def init_scene(self):
        self._scene = QtWidgets.QGraphicsScene()
        self.graphics_view.setScene(self._scene)

        self._scene.addLine(0, 0, 10000, 0, QtGui.QPen(QtGui.QColor(0x21A6FF))).setZValue(30)
        self._scene.addLine(0, -720, 10000, -720, QtGui.QPen(QtGui.QColor(0x21A6FF))).setZValue(30)
        self._scene.addLine(0, 0, 0, -720, QtGui.QPen(QtGui.QColor(0x21A6FF))).setZValue(30)

        self.graphics_view.setSceneRect(-300, -2000, 10000, 2200)

    def init_item(self, qimage, res, pos=(), name='--default--', layer=0):
        i = self.window.generate_identifier()
        item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(qimage))
        self._scene.addItem(item)

        if len(pos) == 0:
            pos = self.graphics_view.mapToScene(600, 300)
            x, y = pos.x(), pos.y()
        elif len(pos) == 2:
            x, y = pos
        else:
            raise ValueError(f'length of parameter "pos" must be 0 or 2, not {len(pos)}')

        item.setX(x)
        item.setY(y)

        item.setAcceptedMouseButtons(Qt.LeftButton)
        item.setCursor(Qt.OpenHandCursor)
        item.setFlags(item.ItemIsMovable | item.ItemIsSelectable)
        item.mousePressEvent = self._get_item_mousepress_callback(i)
        item.mouseMoveEvent = self._get_item_mousemove_callback(item)

        if name == '--default--':
            name = 'struct' + str(i)

        list_item = self.window.obj_list_handler.add_item(name, i)

        item.setZValue(layer)

        self.graphics_view_items[i] = [item, res, qimage, name, layer, list_item]

        return item

    def _get_item_mousepress_callback(self, id_):
        def callback(_):
            self._scene.clearSelection()
            if self._selected_item is not None:
                self.graphics_view_items[self._selected_item][5].setSelected(False)
            self._selected_item = id_
            self.graphics_view_items[self._selected_item][5].setSelected(True)

            self.window.infos_panel_handler.update_structure_infos()
        return callback

    def _get_item_mousemove_callback(self, item):
        mouse_move = item.mouseMoveEvent

        def callback(event):
            x, y = None, None
            if event.modifiers() & Qt.ShiftModifier:
                y = item.y()
            if event.modifiers() & Qt.ControlModifier:
                x = item.x()

            self.window.infos_panel_handler.update_structure_infos()
            to_rtn = mouse_move(event)

            if x is not None:
                item.setX(x)
            if y is not None:
                item.setY(y)

            return to_rtn

        return callback

    def zoom_plus(self):
        self.window.graphics_view.scale(1.25, 1.25)

    def zoom_minus(self):
        self.window.graphics_view.scale(0.8, 0.8)

    def set_bg(self, path=''):
        if not path:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self.window, 'Ouvrir', 'resources/backgrounds',
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
            self._bg_res = os.path.dirname(os.path.relpath(path)).replace('\\', '/').replace('resources/', '')

    def reset_bg(self):
        self._scene.removeItem(self._bg)
        self._bg_res = None
        self._bg = None

    def delete_selected_structure(self):
        if self._selected_item is not None:
            data = self.graphics_view_items[self._selected_item]

            i = self._selected_item
            self._selected_item = None

            self._scene.removeItem(data[0])
            self.graphics_view_items.pop(i)
            self.window.obj_list_handler.refresh_obj_list()

            self.window.infos_panel_handler.update_structure_infos()

