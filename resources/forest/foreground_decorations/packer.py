# -*- coding:Utf-8 -*-

import glob
import os
import shutil
from PIL import Image

for filepath in glob.glob('./*.png'):
    img = Image.open(filepath)
    width, height = img.width, img.height
    dirname = os.path.basename(filepath).replace('.png', '.obj')
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    txt = """
    "dec": [{}, 0],
    "dimensions": [{}, {}],
    "scale2x": 1,
    "image": "{}"
"""
    print(f'creating {dirname}/data.json')
    with open(os.path.join(dirname, 'data.json'), 'w') as file:
        file.write('{' + txt.format(width // 2, width, height, os.path.basename(filepath)) + '}')
    print(f'copying {filepath} into {dirname}')
    shutil.copy(filepath, dirname + '\\')
