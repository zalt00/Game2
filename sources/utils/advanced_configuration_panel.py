# -*- coding:Utf-8 -*-

import os
from .save_modifier import SaveComponent
import sys
import shlex
import traceback
import time
import json


with open(os.path.join(os.path.dirname(__file__), 'config.json')) as datafile:
    full_data = json.load(datafile)
data = full_data['advanced_configuration_panel_data']
del datafile


class BaseApp:
    commands = {}
    modes = {}


def command(name, modes=('base',)):
    def decorator(func):
        for mode in modes:
            if mode not in BaseApp.modes:
                BaseApp.modes[mode] = set()
            BaseApp.modes[mode].add(name)

        BaseApp.commands[name] = func
        return func
    return decorator


class App(BaseApp):

    def __init__(self):

        print('Advanced configuration panel')
        print('Type "help" for more information.')

        self.stop = False

        self.prefix = '> '
        self._mode = 'base'

        self._save_loaded = True

        try:
            self.path = '.\\..\\..\\data\\saves\\save.data'
            SaveComponent.init(self.path)
            SaveComponent.load()

        except FileNotFoundError:
            try:
                self.path = '.\\data\\saves\\save.data'
                SaveComponent.init(self.path)
                SaveComponent.load()
            except FileNotFoundError:
                self.path = ''
                print('internal error: save file was not able to be loaded', file=sys.stderr)
                self._save_loaded = False

    def run(self):
        while not self.stop:
            input_value = input(self.prefix)
            if input_value:
                command_name, *args = shlex.split(input_value)
                if command_name in self.commands and command_name in self.modes[self._mode]:
                    try:
                        self.commands[command_name](self, *args)
                    except Exception:
                        traceback.print_exc()
                else:
                    print('error - no command has this name')

    @command('help', modes=('base', 'edit'))
    def command_help(self):
        """help: shows this message"""
        print('Available commands:')
        for command_name, func in self.commands.items():
            if command_name in self.modes[self._mode]:
                print(f' - {func.__doc__}')

    @command('edit')
    def command_edit(self):
        """edit: activate save editor mode"""
        if self._save_loaded:
            self.display_save_data()
            self.prefix = '(edit)> '
            self._mode = 'edit'
        else:
            print('error - saved data is not loaded, use "load" to load it', file=sys.stderr)

    @command('set', modes=('edit',))
    def command_set_value(self, id_, value, label=None):
        """set <int id> <int|shorts value> <str label (optional)>: set a value"""
        id_ = int(id_)

        if len(value.split(' ')) == 2:
            a, b = map(int, value.split(' '))
            SaveComponent(id_).set_bytes(a, b)
            type_ = 'shorts'
            data['labels'][label] = 'shorts'
        else:
            SaveComponent(id_).set(int(value))
            type_ = 'int'
            data['labels'][label] = 'int'

        if label is not None:
            data['labels'].pop(list(data['labels'])[id_])
            nd = {}
            for i, (k, v) in enumerate(data['labels'].items()):
                if i == id_:
                    nd[label] = type_
                nd[k] = v
        else:
            label = list(data['labels'])[id_]

        self.display_save_data()

    @command('insert', modes=('edit',))
    def command_insert_value(self, id_, label, value):
        """insert <int id> <str label> <int|shorts value>: insert a value"""

        id_ = int(id_)

        SaveComponent.data.insert(id_, 0)
        id_ = min(id_, len(SaveComponent.data) - 1)
        if len(value.split(' ')) == 2:
            a, b = map(int, value.split(' '))
            SaveComponent(id_).set_bytes(a, b)
            type_ = 'shorts'
        else:
            SaveComponent(id_).set(int(value))
            type_ = 'int'

        nd = {}
        for i, (k, v) in enumerate(data['labels'].items()):
            if i == id_:
                nd[label] = type_
            nd[k] = v
        if id_ >= i:
            nd[label] = type_
        data['labels'] = nd
        self.display_save_data()

    @command('quit', modes=('base', 'edit',))
    def command_quit_mode(self):
        """quit: return to base state or quit the panel"""
        if self._mode == 'base':
            answer = input('save before quitting ? ([Y]es|[N]o) ')
            if answer.upper() in ('Y', 'YES'):
                try:
                    self.save()
                except Exception:
                    traceback.print_exc()
                else:
                    time.sleep(0.8)
                    self.quit()
            elif answer.upper() in ('N', 'NO'):
                self.quit()
            else:
                print('error - invalid answer', file=sys.stderr)

        else:
            self._mode = 'base'
            self.prefix = '> '

    def display_save_data(self):
        print(f'Save data for save file {self.path}:')
        i = 0
        for i, (l, t) in enumerate(data['labels'].items()):
            if t == 'shorts':
                value = SaveComponent(i).get_bytes()
            else:
                value = SaveComponent(i).get()
            print(f' - {i} {l}: {value}')
        while len(SaveComponent.data) > i + 1:
            i += 1
            print(f' - {i} <unknown>: {SaveComponent(i).get()}')

    @command('load')
    def command_load(self, *path):
        """load <str path>: load a save file"""
        p = ' '.join(path)
        SaveComponent.init(p)
        SaveComponent.load()
        self.path = p
        print(f'info - save "{p}" was successfully loaded')

    def save(self):
        if self._save_loaded:
            with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'w') as datafile:
                json.dump(full_data, datafile)
            SaveComponent.dump()
            print('info - data successfully saved')
        else:
            print('error - saved data is not loaded, use "load" to load it', file=sys.stderr)

    def quit(self):
        self.stop = True


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


