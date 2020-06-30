# -*- coding:Utf-8 -*-

import xdrlib
from array import array
import os
import sys


class SaveComponent:
    data = None
    path = ""
    menu_save_length = 0
    game_save_length = 0
    
    def __init__(self, i):
        self.i = i

    def _get_index(self, save_id):
        if save_id == 0:
            return self.i
        else:
            return self.menu_save_length + (save_id - 1) * self.game_save_length + self.i

    def get(self, save_id=0):
        return self.data[self._get_index(save_id)]
    
    def get_chars(self, save_id=0):
        a, b = self.get_shorts(save_id)
        return chr(a) + chr(b)
    
    def get_shorts(self, save_id=0):
        index_ = self._get_index(save_id)
        a = self.data[index_] % 256
        b = self.data[index_] >> 8
        return a, b
        
    def set(self, value, save_id=0):
        self.data[self._get_index(save_id)] = value
        
    def set_shorts(self, a, b, save_id=0):
        value = a | (b << 8)
        self.data[self._get_index(save_id)] = value
        
    def set_chars(self, s, save_id=0):
        self.set_shorts(ord(s[0]), ord(s[1]), save_id)
    
    @classmethod
    def init(cls, path, menu_save_length=0, game_save_length=0):
        cls.path = path
        cls.menu_save_length = menu_save_length
        cls.game_save_length = game_save_length
    
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
    
    def __repr__(self):
        return 'SaveComponent({})'.format(self.i)
    
    def __add__(self, value):
        a = SaveCombination()
        a.append(self)
        a.append(value)
        return a


class SaveCombination(list):
    def get(self, save_id=0):
        return tuple((save.get(save_id) for save in self))
    
    def set(self, iterable, save_id=0):
        for value, save in zip(iterable, self):
            save.set(value, save_id)
            
    def get_long(self):
        if len(self) == 2:
            value = self[1].get() | (self[0].get() << 16)
            return value
        raise ValueError("SaveCombination's length must be 2 to call this method")
            
    def __repr__(self):
        return 'SaveCombination({})'.format(super().__repr__())


def main():
    path = input('Please write the path the save.date file: ')
    if path == 'd':
        path = '.\\..\\..\\data\\saves\\save.data'
    SaveComponent.init(path)
    SaveComponent.load()
    labels = []
    with open('save_labels.cfg', 'r') as file:
        for line in file:
            if line:
                labels.append(line.replace('\n', '').split(':'))
    os.system('cls')
    stop = False
    while not stop:
        for i, (l, t) in enumerate(labels):
            if t == 'shorts':
                value = SaveComponent(i).get_shorts()
            else:
                value = SaveComponent(i).get()
            print(f'{i}-{l}: {value}')
        print('\nm: modify a value')
        print('a: add a new value')
        print('r: remove a value')
        print('s: save and quit')
        print('p: python code')
        print('gs: get shorts')
        command = input()
        if command == 's':
            stop = True
            SaveComponent.dump()
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
                SaveComponent(i).set(value)
            elif t == 'shorts':
                value = map(int, input('enter the new value: ').split(' '))
                SaveComponent(i).set_shorts(*value)
            labels[i][1] = t
            
        elif command == 'a':
            i = int(input('enter the id of the new value: '))
            label = input('enter the label of the value: ')
            t = input('enter the type of the value: ')
            labels.insert(i, [label, t])
            SaveComponent.data.insert(i, 0)
            SaveComponent(i).set(0)
            
        elif command == 'r':
            i = int(input('enter the id of the value you want to delete: '))
            labels.pop(i)
            SaveComponent.data.pop(i)
        
        elif command == 'p':
            print('enter your python code: ')
            code = '1'
            while code != 'stop':
                try:
                    exec(code)
                except Exception as e:
                    print(repr(e), file=sys.stderr)
                else:
                    code = input()
                
        elif command == 'gs':
            i = int(input('enter the id of the shorts you want to get: '))
            print(SaveComponent(i).get_shorts())
            input()
            
        os.system('cls')
                
if __name__ == '__main__':
    main()
    
    
    
