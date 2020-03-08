# -*- coding:Utf-8 -*-

import sys
import traceback


class ExceptionWrapper:
    def __init__(self, viewer, logger):
        self.viewer = viewer
        self.logger = logger

    def __enter__(self):
        return

    def __exit__(self, etype, value, tb):
        if etype:
            a = ''.join(traceback.format_exception(etype, value, tb))
            self.logger.critical(value, extra={'traceback': a})
            self.viewer.stop_loop()
            self.viewer.quit()
            sys.exit(-1)            
            
        return False



