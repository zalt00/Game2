# -*- coding:Utf-8 -*-

import glob
import os
import shutil
from PIL import Image

for filepath in glob.glob('./*.obj/*.png'):

    img = Image.open(filepath)
    width, height = img.width, img.height
    dirname = os.path.dirname(filepath)
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    txt = """
    "dec": [0, 0],
    "dimensions": [{1}, {2}],
    "scale2x": 1,
    "image": "{3}"
"""
    print(f'creating {dirname}/data.json')
    new_name = os.path.basename(dirname).replace('.obj', '.png')
    with open(os.path.join(dirname, 'data.json'), 'w') as file:
        file.write('{' + txt.format(width // 2, width, height, new_name) + '}')
    print(f'renaming {filepath} into "{new_name}"')
    img.close()
    os.rename(filepath, os.path.join(dirname, new_name))
