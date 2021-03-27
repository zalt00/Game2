# -*- coding:Utf-8 -*-


from acp.main_window import Window
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    qapp = QApplication([])
    w = Window()
    qapp.exec_()

