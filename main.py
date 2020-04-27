# -*- coding:Utf-8 -*-

import pygame
from profile import run
from pygame.constants import FULLSCREEN, DOUBLEBUF, HWSURFACE, SCALED
from utils.model_loader import get_model
from viewer import window
from controller import app
from utils.exception_wrapper import ExceptionWrapper
from utils.logger import logger
pygame.init()


def main():
    m = get_model('data')
    w = window.Window(
        m.Options.Video.width.get(),
        m.Options.Video.height.get(),
        (FULLSCREEN | HWSURFACE | DOUBLEBUF) * m.Options.Video.display_mode.get() | SCALED)
    a = app.App(w, m)
    w.run()


if __name__ == '__main__':
    main()

