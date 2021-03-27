# -*- coding:Utf-8 -*-

import xdrlib
import os
import sys

try:
    from utils.logger import logger
except ImportError:
    logger = None


# TODO: corriger l'erreur sur la taille des valeurs, il s'agit d'int32 et non d'int16, et peut donc stocker 2 int 16
#       et 32 booleens dans un seul compartiment (c'etait en fait bien get_shorts et non get_bytes)
#       (peu important vu qu'en terme d'espace disque c'est deja tres leger et qu'on voudra rarement stocker
#       des grandes valeurs dans les paires de nombres)

class SaveComponent:
    data = None
    path = ""
    menu_save_length = 0
    game_save_length = 0
    no_dump_mode = False
    
    def __init__(self, i):
        self.i = i

    def _get_index(self, save_id):
        if save_id == 0:
            return self.i
        else:
            return self.menu_save_length + (save_id - 1) * self.game_save_length + self.i

    def get(self, save_id=0):
        return self.data[self._get_index(save_id)]

    def get_booleans(self, save_id=0):
        n = self.get(save_id)
        return self._get_binary(n, 16)

    def get_single_boolean(self, bool_id, save_id=0):
        n = self.get(save_id)
        return (n >> (16 - bool_id - 1)) % 2

    @staticmethod
    def _get_binary(n, size):
        return [(n >> i) % 2 for i in range(size - 1, -1, -1)]

    def get_chars(self, save_id=0):
        a, b = self.get_bytes(save_id)
        return chr(a) + chr(b)
    
    def get_bytes(self, save_id=0):
        n = self.get(save_id)
        a = n % 256
        b = n >> 8
        return a, b
        
    def set(self, value, save_id=0):
        self.data[self._get_index(save_id)] = value

    def set_booleans(self, binary_values, save_id=0):
        value = int(''.join([str(v) for v in binary_values]), base=2)
        self.set(value, save_id)

    def set_single_boolean(self, bool_value, bool_id, save_id=0):
        if self.get_single_boolean(bool_id, save_id) != bool_value:
            n = 32768 >> bool_id
            int_value = self.get(save_id)
            self.set(int_value ^ n, save_id)

    def set_bytes(self, a, b, save_id=0):
        value = a | (b << 8)
        self.set(value, save_id)
        
    def set_chars(self, s, save_id=0):
        self.set_bytes(ord(s[0]), ord(s[1]), save_id)
    
    @classmethod
    def init(cls, path, menu_save_length=0, game_save_length=0, no_dump_mode=False):
        cls.path = path
        cls.menu_save_length = menu_save_length
        cls.game_save_length = game_save_length
        cls.no_dump_mode = no_dump_mode

    @classmethod
    def load(cls):
        if logger is not None:
            logger.debug('Loading save from disk')
        with open(cls.path, 'rb') as file:
            up = xdrlib.Unpacker(file.read())
        cls.data = up.unpack_array(up.unpack_int)
        up.done()
    
    @classmethod
    def dump(cls):
        if not cls.no_dump_mode:
            if logger is not None:
                logger.debug('Dumping save to disk')
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
            
    def get_int(self):
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
                value = SaveComponent(i).get_bytes()
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
                SaveComponent(i).set_bytes(*value)
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
            print(SaveComponent(i).get_bytes())
            input()
            
        os.system('cls')


if __name__ == '__main__':
    main()
    

