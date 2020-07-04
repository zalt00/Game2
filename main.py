# -*- coding:Utf-8 -*-

import pygame
from profile import run
from pygame.constants import FULLSCREEN, DOUBLEBUF, HWSURFACE, SCALED
from utils.model_loader import get_model
from viewer import window
from controller import app
from utils.exception_wrapper import ExceptionWrapper
import utils.logger as lg
import argparse
import pyglet
import sys
pygame.init()


def main():
    lg.logger.info('Imports succeeded, starting program')
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="activate debug mode", action="store_true")
    args = parser.parse_args()

    debug = args.debug
    if debug:
        lg.logger.info('Launching in debug mode')
        lg.activate_debug_mode()
    m = get_model('data')
    w = window.Window(
        m.Options.Video.width.get(),
        m.Options.Video.height.get())
    a = app.App(w, m, debug=debug)
    lg.logger.info('Interfaces created successfully, starting main loop')
    with ExceptionWrapper(w, lg.logger):
        pyglet.app.run()


if __name__ == '__main__':
    main()

