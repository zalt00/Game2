# -*- coding:Utf-8 -*-

from pyglet.input import get_joysticks


class Joystick(pyglet.input.Joystick):
    def __init__(self, device, on_joyaxis_motion, on_joyhat_motion, on_joybutton_press, on_joybutton_release):
        super().__init__(device)


