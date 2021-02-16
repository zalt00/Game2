# -*- coding:Utf-8 -*-

import yaml


with open('data/map_editor_data/config.yml') as _configfile:
    config = yaml.safe_load(_configfile)
del _configfile

