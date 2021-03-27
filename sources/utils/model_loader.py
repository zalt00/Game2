# -*- coding:Utf-8 -*-

import sys
import os
from utils.save_modifier import SaveComponent


def get_model(path, default_save=False):
    sys.path.append(path)
    from data.data_ import Data
    if default_save:
        SaveComponent.init(os.path.normpath(Data.default_save_path), Data.menu_save_length, Data.game_save_length,
                           no_dump_mode=True)
    else:
        SaveComponent.init(os.path.normpath(Data.save_path), Data.menu_save_length, Data.game_save_length)
    SaveComponent.load()
    return Data

