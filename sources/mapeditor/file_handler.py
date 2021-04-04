# -*- coding:Utf-8 -*-


import yaml
from PyQt5 import QtWidgets
import os
import copy
import sqlite3
from .config import config


class FileHandler:
    def __init__(self, window):
        self.window = window

        self.template_data = self.window.template_data
        self.db = sqlite3.connect(config['collision_database_path'])
        self.cursor = self.db.cursor()
        self._map_path = None

        with open(config['structure_data_path']) as datafile:
            self.additional_structure_data = yaml.safe_load(datafile)

    @property
    def map_path(self):
        return self._map_path

    @map_path.setter
    def map_path(self, value):
        if isinstance(value, str):
            self.window.setWindowTitle(os.path.basename(value))
            self._map_path = value
        elif value is None:
            self.window.setWindowTitle('Map editor')
            self._map_path = None
        else:
            raise TypeError('invalid type for "value": should be NoneType or string')

    def add_collision_data(self, res, ground, walls):
        try:
            self.cursor.execute("INSERT INTO COLLISIONS (res, ground, walls) values (?, ?, ?);", (res, ground, walls))
        except sqlite3.IntegrityError:
            self.cursor.execute("UPDATE COLLISIONS SET ground = ?, walls = ? WHERE res = ?", (ground, walls, res))
        self.db.commit()

    def get_raw_collision_data(self, res):
        data = self.cursor.execute('SELECT * FROM COLLISIONS WHERE res = ?', (res,))
        data = list(data)
        if len(data) == 0:
            return {}
        data = data[0]
        return dict(ground=data[1], walls=data[2])

    def get_collision_data(self, res):
        raw_data = self.get_raw_collision_data(res)
        if raw_data == {}:
            return {}

        # format: ax1*ay1+bx1*by1|ax2*ay2+bx2*by2
        if raw_data['ground']:
            ground = [[[int(coord) for coord in points.split('*')]
                       for points in segments.split('+')] for segments in raw_data['ground'].split('|')]
        else:
            ground = []
        if raw_data['walls']:
            walls = [[[int(coord) for coord in points.split('*')]
                      for points in segments.split('+')] for segments in raw_data['walls'].split('|')]
        else:
            walls = []
        return dict(ground=ground, walls=walls)

    def _open(self, path):
        with open(path) as datafile:
            data = yaml.safe_load(datafile)

        self.window.clear_objects()

        constraints = self.window.constraint_panel_handler.constraints
        while len(constraints) != 0:
            constraints[-1].remove()

        checkpoints = self.window.checkpoint_panel_handler.checkpoints
        while len(checkpoints) != 0:
            checkpoints[-1].remove()

        for obj_data in data['objects_data'].values():
            if obj_data['type'] == 'structure':
                qimage = self.window.load_image(obj_data['res'], self.window.edit_panel_handler.palette)
                pos = obj_data['pos']

                kinematic = obj_data.get('kinematic', False)

                item = self.window.scene_handler.init_item(qimage, obj_data['res'],
                                                           name=obj_data['name'],
                                                           layer=obj_data['layer'],
                                                           kinematic=kinematic)
                rect = item.boundingRect()
                item.setX(self.window.datax2canvasx(pos[0], rect))
                item.setY(self.window.datay2canvasy(pos[1], rect))

            elif obj_data['type'] == 'constraint':
                self.window.constraint_panel_handler.add_constraint(
                    name=obj_data['name'],
                    anchor_a=obj_data['anchor_a'],
                    anchor_b=obj_data['anchor_b'],
                    object_a=obj_data['object_a'],
                    object_b=obj_data['object_b']
                )

        if 'triggers_data' in data:
            self.window.trigger_panel_handler.init_triggers_data(data['triggers_data'])

        if 'checkpoints' in data:
            self.window.checkpoint_panel_handler.set_data(data['checkpoints'])

        self.window.scene_handler.set_bg(path=os.path.join('resources/', data['background_data']['res'], 'preview.png'))

    def _save(self, path):
        data = copy.deepcopy(self.template_data)

        for item_data in self.window.scene_handler.graphics_view_items.values():
            res = item_data[1]
            name = item_data[3]
            layer = item_data[4]
            item = item_data[0]
            kinematic = item_data[6]

            rect = item.boundingRect()
            x = self.window.canvasx2datax(item.x(), rect)
            y = self.window.canvasy2datay(item.y(), rect)

            obj_data = dict()
            data['objects_data'][name + '_structure'] = obj_data

            obj_data['res'] = res
            obj_data['type'] = 'structure'
            obj_data['state'] = 'base'
            obj_data['is_built'] = res.endswith('.obj')
            obj_data['name'] = name

            collision_data = self.get_collision_data(res)
            if collision_data:
                obj_data['walls'] = collision_data['walls']
                obj_data['ground'] = collision_data['ground']

            obj_data['pos'] = [x, y]
            obj_data['layer'] = layer

            if kinematic:
                obj_data['kinematic'] = True

            families = self._get_struct_families(res, self.additional_structure_data['structure_families'])
            for family_name in families:
                family = self.additional_structure_data['structure_families'][family_name]
                for key, value in family['data'].items():
                    obj_data[key] = value

            if res in self.additional_structure_data:
                for key, value in self.additional_structure_data[res].items():
                    obj_data[key] = value

        constraint_data = self.window.constraint_panel_handler.get_data(data['objects_data'])
        data['objects_data'].update(constraint_data)

        data['background_data']['res'] = self.window.scene_handler.bg_res

        data['triggers_data'] = self.window.trigger_panel_handler.get_triggers_data()
        data['checkpoints'] = self.window.checkpoint_panel_handler.get_data()

        with open(path, 'w') as datafile:
            yaml.safe_dump(data, datafile)

        print('info - level successfully saved')

    @staticmethod
    def _get_struct_families(res, families_data):
        families = set()
        for family_name, family_data in families_data.items():
            if any([res.startswith(component) for component in family_data['components']]):
                families.add(family_name)
        return families

    def save_as(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.window, 'Sauvegarder sous', 'data/maps',
                                                        "Yaml file (*.yml);;Tous les fichiers (*)")
        if path:
            if not path.endswith('.yml'):
                path += '.yml'
            path = path.replace('\\', '/')
            self._save(path)

            self.map_path = path

        return path

    def save(self):
        if self.map_path is not None:
            self._save(self.map_path)
            return True
        else:
            return self.save_as()

    def open(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self.window, 'Ouvrir', 'data/maps',
                                                        "Yaml file (*.yml);;Tous les fichiers (*)")
        if os.path.exists(path) and path.endswith('.yml'):
            path = path.replace('\\', '/')
            self._open(path)
            self.map_path = path
