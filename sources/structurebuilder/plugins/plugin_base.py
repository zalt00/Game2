# -*- coding:Utf-8 -*-


from types import MethodType

commands = []


def command(func_or_binding, *bindings):
    if isinstance(func_or_binding, str):
        binding = (func_or_binding,) + tuple(bindings)

        def decorator(func):
            commands.append(func)
            func.binding = binding
            return func
        return decorator

    elif callable(func_or_binding):
        commands.append(func_or_binding)
        func_or_binding.binding = ()
        return func_or_binding


class PluginMeta(type):
    def __init__(cls, name, bases, dict_):
        super(PluginMeta, cls).__init__(name, bases, dict_)
        if not hasattr(cls, "commands"):
            cls.commands = {}
        cls.commands.update({c.__name__: c for c in commands})
        commands[:] = []


class AbstractPlugin:
    def __init__(self, app):
        self.app = app


