# -*- coding:Utf-8 -*-

from pygame.constants import FULLSCREEN, DOUBLEBUF, HWSURFACE, OPENGL
from utils.model_loader import get_model
from viewer import window
from controller import app
from utils.exception_wrapper import ExceptionWrapper
from utils.logger import logger

if __name__ == '__main__':
    m = get_model('data')
    w = window.Window(
        m.Options.Video.width.get(),
        m.Options.Video.height.get(),
        (FULLSCREEN | DOUBLEBUF | HWSURFACE) * m.Options.Video.display_mode.get())
    a = app.App(w, m)
    if m.Options.Video.display_mode.get():
        with ExceptionWrapper(w, logger):
            w.run()
    else:
        w.run()


