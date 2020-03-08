# -*- coding:Utf-8 -*-

import sys


def get_model(path):
    sys.path.append(path)
    from data_ import Data
    return Data

