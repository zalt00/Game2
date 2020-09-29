# -*- coding:Utf-8 -*-


import pyglet
import numpy as np
from PIL import Image


img = Image.open('img.png')
a = np.array(img)
image = pyglet.image.ImageData(640, 368, 'RGBA', a.tobytes(), -640 * 4).get_texture()

print(a.shape)

sprite = pyglet.sprite.Sprite(image)
sprite.scale = 2
window = pyglet.window.Window(800, 600)


@window.event
def on_draw():
    sprite.draw()


pyglet.app.run()
