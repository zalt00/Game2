# -*- coding:Utf-8 -*-

import dataclasses
from typing import Any, Callable
from utils.types import DataContainer


@dataclasses.dataclass
class MenuActionManagerData:

    # BaseMenuActionManager
    window: Any
    buttons: set
    classic_buttons: dict
    classic_buttons_order: tuple
    panels: dict
    panel_order: tuple
    additional_texts: dict
    additional_structures: dict

    # MainMenuActionManager
    play_callback: Callable
    quit_game_callback: Callable
    open_options_callback: Callable

    # OptionsActionManager
    return_to_mainmenu_callback: Callable
    change_kb_ctrls_callback: Callable
    change_con_ctrls_callback: Callable
    set_ctrl_callback: Callable
    options_data: DataContainer
    reinit_page_callback: Callable
    set_fullscreen_callback: Callable

    # CharacterSelectionActionManager
    start_game_callback: Callable


