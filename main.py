# -*- coding:Utf-8 -*-

import pygame
from profile import run
from pygame.constants import FULLSCREEN, DOUBLEBUF, HWSURFACE, SCALED
from utils.model_loader import get_model
from viewer import window
from controller import app
from utils.exception_wrapper import ExceptionWrapper
from utils.logger import logger
import argparse
import sys
pygame.init()


def main():
    logger.info('Imports succeeded, starting program')
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="activate debug mode", action="store_true")
    args = parser.parse_args()

    debug = args.debug
    if debug:
        logger.info('Launching in debug mode')
    m = get_model('data')
    w = window.Window(
        m.Options.Video.width.get(),
        m.Options.Video.height.get(),
        (FULLSCREEN | HWSURFACE | DOUBLEBUF) * m.Options.Video.display_mode.get() | SCALED)
    a = app.App(w, m, debug=debug)
    logger.info('Interfaces created successfully, starting main loop')
    with ExceptionWrapper(w, logger):
        w.run()


if __name__ == '__main__':
    main()

