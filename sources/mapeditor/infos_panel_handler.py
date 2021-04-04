# -*- coding:Utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt


class InfosPanelHandler:

    _alpha = 'abcdefghijklmnopqrstuvwxyz'
    AUTHORIZED_CHARS = _alpha + _alpha.upper() + '0123456789_'
    del _alpha

    def __init__(self, window):
        self.window = window
        self._updating_structure_infos = False

        self._preview_scene = QtWidgets.QGraphicsScene()
        self.window.preview_graphics_view.setScene(self._preview_scene)

    def apply_structure_infos_changes(self, *_, **__):
        if not self._updating_structure_infos:
            if self.window.scene_handler.selected_item is not None:
                data = self.window.scene_handler.graphics_view_items.get(self.window.scene_handler.selected_item, None)
                if data is not None:
                    text = self.window.name_lineedit.text()
                    if len(text) == 0:
                        text = 'unnamed'
                    new_text = ''
                    for char in text:
                        if char not in self.AUTHORIZED_CHARS:
                            new_text += '_'
                        else:
                            new_text += char

                    if new_text[0] in '0123456789':
                        new_text = '_' + new_text

                    data[3] = new_text
                    data[4] = self.window.layer_spinbox.value()
                    data[0].setZValue(data[4])

                    rect = data[0].boundingRect()
                    data[0].setX(self.window.datax2canvasx(self.window.x_spinbox.value(), rect))
                    data[0].setY(self.window.datay2canvasy(self.window.y_spinbox.value(), rect))

                    data[5].setText(data[3])

                    data[6] = self.window.is_kinematic_checkbox.isChecked()

                    self.update_structure_infos()

    def update_structure_infos(self):
        self._updating_structure_infos = True
        self._preview_scene.clear()
        if self.window.scene_handler.selected_item is not None:
            data = self.window.scene_handler.graphics_view_items[self.window.scene_handler.selected_item]

            self._preview_scene.addPixmap(QtGui.QPixmap(data[2]))

            self.window.resource_label.setText(data[1])

            self.window.name_lineedit.setText(data[3])

            self.window.layer_spinbox.setValue(data[4])

            self.window.is_kinematic_checkbox.setChecked(data[6])

            rect = data[0].boundingRect()
            x, y = int(data[0].x()), int(data[0].y())

            self.window.x_spinbox.setValue(x + int(rect.width()) // 2)
            bottom = -(int(rect.bottom()) + y)
            self.window.y_spinbox.setValue(bottom)

            left = int(rect.left()) + x
            right = int(rect.right()) + x
            top = -(int(rect.top()) + y)
            self.window.bbox_label.setText(f'{left}, {bottom}, {right}, {top}')

        self._updating_structure_infos = False

