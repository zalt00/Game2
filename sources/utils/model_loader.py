# -*- coding:Utf-8 -*-

import sys
import os
from utils.save_modifier import Save


def get_model(path):
    sys.path.append(path)
    from data.data_ import Data
    Save.init(os.path.join(path, 'save.data'))
    Save.load()
    return Data

