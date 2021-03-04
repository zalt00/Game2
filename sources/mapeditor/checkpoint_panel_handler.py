# -*- coding:Utf-8 -*-


from PyQt5 import QtWidgets
from .checkpoint_panel_widgets import Checkpoint


class CheckpointPanelHandler:
    def __init__(self, window):
        self.window = window

        self.checkpoints = []

    def add_checkpoint(self):
        self._add_checkpoint()

    def apply_changes(self):
        for widget in self.checkpoints:
            widget.update_data()

    def get_remove_checkpoint_callback(self, id_):
        def remove_checkpoint():
            widget = self.checkpoints[id_]
            self.window.checkpoint_scroll_area_content.layout().removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()

            self.checkpoints.pop(id_)

            self.update_checkpoints_identifiers()
        return remove_checkpoint

    def update_checkpoints_identifiers(self):
        for id_, widget in enumerate(self.checkpoints):
            widget.id_ = id_
            widget.update_widget()
            widget.remove_callback = self.get_remove_checkpoint_callback(id_)

    def _add_checkpoint(self, id_=-1, x=0, y=0):
        if id_ == -1:
            id_ = len(self.checkpoints)
        widget = Checkpoint(id_, self.get_remove_checkpoint_callback(id_), x, y)
        self.window.checkpoint_scroll_area_content.layout().addWidget(widget)
        self.checkpoints.append(widget)

    def get_data(self):
        data = []

        for widget in self.checkpoints:
            name = f'checkpoint{widget.id_}'
            pos = (widget.x, widget.y)
            data.append((name, pos))
        return data

    def set_data(self, data):
        for i, (_, pos) in enumerate(data):
            self._add_checkpoint(i, pos[0], pos[1])




