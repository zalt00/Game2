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
from PyQt5 import QtCore
from utils.save_modifier import SaveComponent
from utils.model_loader import get_model
import os
import sys
import re
import json
import qimage2ndarray
import yaml
from .save_editor_widgets import SaveComponentGroup, SaveComponentWidget

dir_path = '\\'.join(__file__.split('\\')[:-1])


class Window(QMainWindow):
    def __init__(self, path=''):
        super().__init__()
        uic.loadUi('.\\qt_templates\\advanced_configuration_panel.ui', self)
        self.show()

        self.model = get_model('data/')

        data_length = len(SaveComponent.data)

        game_saves_length = data_length - self.model.menu_save_length
        number_of_game_saves = game_saves_length // self.model.game_save_length
        if game_saves_length % self.model.game_save_length != 0:
            number_of_game_saves += 1

        layout = self.scroll_area_content.layout()

        self.save_component_widgets = []

        with open('data/acp_data/labels.json', 'r') as datafile:
            self.labels = json.load(datafile)

        with open('data/acp_data/dtypes.json', 'r') as datafile:
            self.dtypes = json.load(datafile)

        self.menu_group = SaveComponentGroup('Menu')
        layout.addWidget(self.menu_group)

        for i in range(self.model.menu_save_length):
            w = SaveComponentWidget(self.labels[str(hash((i, 0)))], self.dtypes[str(hash((i, 0)))], i, 0)
            self.menu_group.add_widget(w)
            self.save_component_widgets.append(w)

        self.games_save_groups = [None] * number_of_game_saves

        for game_save_id in range(number_of_game_saves):
            save_id = game_save_id + 1

            group = SaveComponentGroup(f'Game, save {save_id}')
            layout.addWidget(group)
            self.games_save_groups[game_save_id] = group

            for i in range(self.model.game_save_length):
                if i + self.model.menu_save_length + game_save_id * self.model.game_save_length < len(
                        SaveComponent.data):
                    w = SaveComponentWidget(self.get_label(i, save_id), 'integer', i, save_id)
                    group.add_widget(w)
                    self.save_component_widgets.append(w)

        self.action_save_labels.triggered.connect(self.save_label_and_dtypes)
        self.action_save.triggered.connect(self.save)
        self.action_reload.triggered.connect(self.reload)
        self.action_new_save_component.triggered.connect(self.new_save_component)
        self.action_pop_last.triggered.connect(self.pop_last)

    def get_label(self, i, save_id):
        try:
            return self.labels[str(hash((i, save_id)))]
        except KeyError:
            return 'unnamed'

    def pop_last(self):
        w = self.save_component_widgets.pop()

        w.setParent(None)

        if len(self.games_save_groups) > 0:
            self.games_save_groups[-1].remove_widget(w)

            if len(self.games_save_groups[-1].widgets) == 0:
                self.games_save_groups[-1].setParent(None)
                self.games_save_groups.pop()

        SaveComponent.data.pop()

    def new_save_component(self):
        SaveComponent.data.append(0)
        global_id = len(SaveComponent.data) - 1
        if global_id < self.model.menu_save_length:
            save_id = 0
            id_ = global_id
            group = self.menu_group
        else:
            id_ = global_id - self.model.menu_save_length
            save_id = id_ // self.model.game_save_length + 1

            id_ %= self.model.game_save_length

            try:
                group = self.games_save_groups[save_id - 1]
            except IndexError:
                group = SaveComponentGroup(f'Game, save {save_id}')
                self.scroll_area_content.layout().addWidget(group)

                self.games_save_groups.append(group)

        w = SaveComponentWidget('new component', 'integer', id_, save_id)
        group.add_widget(w)
        self.save_component_widgets.append(w)

    def save(self):

        for w in self.save_component_widgets:
            w.apply_on_save_component()

        SaveComponent.dump()

    def reload(self):
        SaveComponent.load()

        for w in self.save_component_widgets:
            w.refresh_value()

    def save_label_and_dtypes(self):
        self.save_labels()
        self.save_dtypes()

    def save_dtypes(self):

        for w in self.save_component_widgets:
            w.update_dtype(self.dtypes)

        with open('data/acp_data/dtypes.json', 'w') as datafile:
            json.dump(self.dtypes, datafile)

    def save_labels(self):

        for w in self.save_component_widgets:
            w.update_label(self.labels)

        with open('data/acp_data/labels.json', 'w') as datafile:
            json.dump(self.labels, datafile)






