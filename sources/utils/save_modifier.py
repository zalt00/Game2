# -*- coding:Utf-8 -*-

import xdrlib
from array import array


class Save:
    data = None
    
    def __init__(self, i):
        self.i = i
    
    def get(self):
        return self.data[self.i]
    
    def set(self, value):
        self.data[self.i] = value    
    
    @classmethod
    def load(cls, path):
        with open(path, 'rb') as file:
            up = xdrlib.Unpacker(file.read())
        cls.data = up.unpack_array(up.unpack_int)
        up.done()
        
    @classmethod
    def dump(cls, path):
        p = xdrlib.Packer()
        p.pack_array(cls.data, p.pack_int)
        b = p.get_buffer()
        with open(path, 'wb') as file:
            file.write(b)
            
def set_to_default(path):
    Save.data = array('i', [200, 500, 0])
    Save.dump(path)
