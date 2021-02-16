# -*- coding:Utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt


class ObjListHandler:
    def __init__(self, window):
        self.window = window
        self.obj_list = self.window.obj_list

        self._list_item_to_id = {}

    def refresh_obj_list(self):
        self.obj_list.clear()
        self._list_item_to_id.clear()
        for i, data in self.window.scene_handler.graphics_view_items.items():
            list_item = QtWidgets.QListWidgetItem(data[3])
            self.obj_list.addItem(list_item)

            self.window.scene_handler.graphics_view_items[i][5] = list_item

            self._list_item_to_id[id(list_item)] = i

    def change_selection_in_scene(self, current, previous):
        try:
            id_ = self._list_item_to_id[id(current)]
        except KeyError:
            pass
        else:
            self.window.scene_handler.graphics_view_items[id_][0].setSelected(True)
            if self.window.scene_handler.selected_item is not None:
                self.window.scene_handler.graphics_view_items[
                    self.window.scene_handler.selected_item][0].setSelected(False)
            self.window.scene_handler.selected_item = id_
            self.window.infos_panel_handler.update_structure_infos()

    def add_item(self, name, i):
        list_item = QtWidgets.QListWidgetItem(name)
        self.obj_list.addItem(list_item)
        self._list_item_to_id[id(list_item)] = i
        return list_item



