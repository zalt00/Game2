# -*- coding:Utf-8 -*-

import json


def get_model(path):
    with open(path, 'r') as file:
        model = json.load(file)
    return model

