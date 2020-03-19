# -*- coding:Utf-8 -*-

from pygame.constants import FULLSCREEN
from utils.model_loader import get_model
from viewer import window
from controller import app
from utils.exception_wrapper import ExceptionWrapper
from utils.logger import logger

if __name__ == '__main__':
    m = get_model('data/')
    w = window.Window(1280, 720, FULLSCREEN * 1)
    a = app.App(w, m)
    with ExceptionWrapper(w, logger):
        w.run()


