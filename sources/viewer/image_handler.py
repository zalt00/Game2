# -*- coding:Utf-8 -*-


class ImageHandler:
    def __init__(self, res):
        self.res = res
        
    def update_image(self, _):
        raise NotImplementedError

class BgLayerImageHandler(ImageHandler):
    def update_image(self, sprite):
        return self.res[sprite.layer]
