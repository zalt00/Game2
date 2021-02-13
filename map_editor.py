# -*- coding:Utf-8 -*-

from mapeditor.app import Window
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = ''
    app = QApplication([])
    window = Window(path)
    app.exec_()
