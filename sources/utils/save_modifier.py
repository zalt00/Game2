# -*- coding:Utf-8 -*-

import xdrlib
from array import array
import os


class Save:
    data = None
    path = ""
    
    def __init__(self, i):
        self.i = i
    
    def get(self):
        return self.data[self.i]
    
    def get_chars(self):
        a, b = self.get_shorts()
        return chr(a) + chr(b)
    
    def get_shorts(self):
        a = self.data[self.i] % 256
        b = self.data[self.i] >> 8
        return a, b
        
    def set(self, value):
        self.data[self.i] = value
        
    def set_shorts(self, a, b):
        value = a | (b << 8)
        self.data[self.i] = value
        
    def set_chars(self, s):
        self.set_shorts(ord(s[0]), ord(s[1]))
    
    @classmethod
    def init(cls, path):
        cls.path = path
    
    @classmethod
    def load(cls):
        with open(cls.path, 'rb') as file:
            up = xdrlib.Unpacker(file.read())
        cls.data = up.unpack_array(up.unpack_int)
        up.done()
    
    @classmethod
    def dump(cls):
        p = xdrlib.Packer()
        p.pack_array(cls.data, p.pack_int)
        b = p.get_buffer()
        with open(cls.path, 'wb') as file:
            file.write(b)

            
def set_to_default(path):
    Save.data = array('i', [200, 500, 0])
    Save.dump(path)


def main():
    path = input('Please write the path the save.date file: ')
    if path == 'd':
        path = '.\\..\\..\\data\\save.data'
    Save.init(path)
    Save.load()
    labels = []
    with open('save_labels.cfg', 'r') as file:
        for line in file:
            if line:
                labels.append(line.replace('\n', '').split(':'))
    os.system('cls')
    stop = False
    while not stop:
        print(*(f'{i}-{l}: {value} ({t})' for (i, (l, t)), value in zip(enumerate(labels), Save.data)), sep='\n', end='\n\n')
        print('m: modify a value')
        print('a: add a new value')
        print('r: remove a value')
        print('s: save and quit')
        print('p: python code')
        print('gs: get shorts')
        command = input()
        if command == 's':
            stop = True
            Save.dump()
            txt = '\n'.join((':'.join(l) for l in labels))
            with open('save_labels.cfg', 'w') as file:
                file.write(txt)
                
        elif command == 'm':
            i = int(input('enter the id of the value you want to modify: '))
            t = input('enter the type of the value (int/shorts): ')
            if t == '':
                t = labels[i][1]
            if t == 'int':
                value = int(input('enter the new value: '))
                Save(i).set(value)
            elif t == 'shorts':
                value = map(int, input('enter the new value: ').split(' '))
                Save(i).set_shorts(*value)
            labels[i][1] = t
            
        elif command == 'a':
            i = int(input('enter the id of the new value: '))
            label = input('enter the label of the value: ')
            t = input('enter the type of the value: ')
            labels.insert(i, [label, t])
            Save.data.insert(i, 0)
            Save(i).set(0)
            
        elif command == 'r':
            i = int(input('enter the id of the value you want to delete: '))
            labels.pop(i)
            Save.data.pop(i)
        
        elif command == 'p':
            print('enter your python code: ')
            code = '1'
            while code != 'stop':
                exec(code)
                code = input()
                
        elif command == 'gs':
            i = int(input('enter the id of the shorts you want to get: '))
            print(Save(i).get_shorts())
            input()
            
        os.system('cls')
                
if __name__ == '__main__':
    main()
    
    
    
