# -*- coding:Utf-8 -*-

from pygame.constants import FULLSCREEN
from model import model_loader
from viewer import window
from controller import app

if __name__ == '__main__':
    m = model_loader.get_model('data/model.json')
    w = window.Window(1600, 900, FULLSCREEN)
    a = app.App(w, m)
    w.run()
