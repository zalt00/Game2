# -*- coding:Utf-8 -*-


import pyglet
from pyglet.gl import gl

pyglet.image.Texture.default_min_filter = gl.GL_NEAREST
pyglet.image.Texture.default_mag_filter = gl.GL_NEAREST

pyglet.resource.path = ['']
pyglet.resource.reindex()

img = pyglet.resource.image('img.png')
batch = pyglet.graphics.Batch()
sprite = pyglet.sprite.Sprite(img, batch=batch)
sprite.scale = 3

window = pyglet.window.Window(1500, 800)

@window.event
def on_draw():
    batch.draw()

pyglet.app.run()