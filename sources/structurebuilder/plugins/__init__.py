# -*- coding:Utf-8 -*-

import importlib
import sys

sys.path.append(__file__.replace('__init__.py', ''))


with open(__file__.replace('__init__.py', 'plugins.txt')) as _datafile:
    plugin_names = [_name.replace('\n', '') for _name in _datafile]

for _plugin_name in plugin_names:
    globals()[_plugin_name] = importlib.import_module('.' + _plugin_name + '_plugin', __package__)
