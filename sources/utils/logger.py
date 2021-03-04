# -*- coding:Utf-8 -*-

import os
import logging as lg
from logging.handlers import RotatingFileHandler


def get_logger():
    _logger = lg.getLogger('main')
    _logger.setLevel(lg.DEBUG)

    formatter = lg.Formatter()

    file_handler = RotatingFileHandler('platformer.log', 'a', 1000000, 1)

    file_handler.setLevel(lg.INFO)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    stream_handler = lg.StreamHandler()

    stream_handler.setLevel(lg.DEBUG)
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)

    return _logger


class GameLogger:
    def __init__(self):
        self.logger = lg.getLogger('main')
        self.logger.setLevel(lg.DEBUG)

        self.base_directory = os.path.normpath(os.environ.get('base', '.\\'))

        self.base_handler = RotatingFileHandler(self.base_directory + '\\logs\\main.log',
                                                'a', 1000000, 1, encoding='utf8')
        self.error_handler = lg.FileHandler(self.base_directory + '\\logs\\main.error.log', encoding='utf8')
        self.stream_handler = lg.StreamHandler()

        fmtb = lg.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        fmterr = lg.Formatter('''{0} %(levelname)s {0}
at %(asctime)s, line %(lineno)s :
%(traceback)s'''.format('-' * 30))

        self.base_handler.setFormatter(fmtb)
        self.base_handler.setLevel(lg.INFO)

        self.stream_handler.setFormatter(fmtb)
        self.stream_handler.setLevel(lg.INFO)

        self.error_handler.setFormatter(fmterr)
        self.error_handler.setLevel(lg.ERROR)

        self.logger.addHandler(self.base_handler)
        self.logger.addHandler(self.stream_handler)
        self.logger.addHandler(self.error_handler)


_logger = GameLogger()
logger = _logger.logger


def activate_debug_mode():
    _logger.stream_handler.setLevel(lg.DEBUG)



