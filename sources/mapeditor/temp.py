# -*- coding:Utf-8 -*-

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
from viewer.resources_loader import ResourcesLoader

import dataclasses

dir_path = '\\'.join(__file__.split('\\')[:-1])


class Window(QMainWindow):
    def __init__(self, path=''):
        super().__init__()
        #uic.loadUi('.\\qt_templates\\mapeditor_mwin.ui', self)
        self.show()

        QtWidgets.QFileDialog.getOpenFileName(self)


app = QApplication([])
window = Window()
app.exec_()


