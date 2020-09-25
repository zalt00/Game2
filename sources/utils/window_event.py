# -*- coding:Utf-8 -*-


def event(func):
    event_name = func.__name__

    def callback(self, *args, **kwargs):
        self.event_manager.do(event_name, *args, **kwargs)

    callback.__name__ = event_name
    return callback

