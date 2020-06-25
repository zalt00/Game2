# -*- coding:Utf-8 -*-

import sys
import os
from utils.save_modifier import SaveComponent


def get_model(path):
    sys.path.append(path)
    from data.data_ import Data
    SaveComponent.init(os.path.normpath(Data.save_path), Data.menu_save_length, Data.game_save_length)
    SaveComponent.load()
    return Data

