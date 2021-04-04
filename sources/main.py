# -*- coding:Utf-8 -*-

from cProfile import run
from utils.model_loader import get_model
from viewer import window
from controller import app
from utils.exception_wrapper import ExceptionWrapper
import utils.logger as lg
import argparse
import pyglet
import sys


PROFILING = False


def main():
    lg.logger.info('Imports succeeded, starting program')
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="activate debug mode", action="store_true")
    parser.add_argument("-m", "--map", help="launch the game at a specific map", type=str)
    args = parser.parse_args()

    debug = args.debug
    if debug:
        lg.logger.info('Launching in debug mode')
        lg.activate_debug_mode()
    m = get_model('data', default_save=args.map is not None)
    w = window.Window(
        m.Options.Video.width.get(),
        m.Options.Video.height.get(),
        m.Options.Video.display_mode.get())
    a = app.App(w, m, debug=debug)
    lg.logger.info('Interfaces created successfully, starting main loop')

    if args.map is not None:
        m.Game.maps = (args.map,)
        a.start_game(1, map_test_mode=True)

    with ExceptionWrapper(w, lg.logger):
        if PROFILING:
            run('pyglet.app.run()', sort='cumtime')
        else:
            pyglet.app.run()


if __name__ == '__main__':
    main()

