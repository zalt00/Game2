# -*- coding:Utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
import glob
import qimage2ndarray
import os, sys
import dataclasses
from subprocess import Popen, PIPE
import time


@dataclasses.dataclass
class ItemData:
    res: str
    qimage: QtGui.QImage


class EditPanelHandler:
    def __init__(self, window):
        self.window = window
        self._resource_loader = self.window.resource_loader
        self.palette = None
        self.biome = None
        self._struct_lists = None
        self._item_to_data = {}

        self._tab_id_to_resource_name_template = [
            'structures/mainbuilds/{biome}/{name}',
            'structures/background_decorations/{biome}/{name}',
            'structures/dynamic_structures/{biome}/{name}',
            'structures/spikes/{biome}/{name}',
            'decorations/{biome}/{name}',
            'foreground_decorations/{biome}/{name}',
            'special_objects/{name}'
        ]
        self._tab_id_to_structure_type = [
            'mainbuilds',
            'background_decorations',
            'dynamic_structures',
            'spikes',
            'decorations',
            'foreground_decorations',
            'special_objects'
        ]

    @property
    def struct_lists(self):
        return self._struct_lists

    def init_struct_lists(self, biome, palette):
        self.palette = self._resource_loader.load(palette)
        self.biome = biome

        self._struct_lists = dict(
            mainbuilds=self.window.mb_struct_list,
            background_decorations=self.window.bgd_struct_list,
            dynamic_structures=self.window.ds_struct_list,
            spikes=self.window.sk_struct_list,
            decorations=self.window.dec_struct_list,
            foreground_decorations=self.window.fgd_struct_list,
            special_objects=self.window.so_struct_list
        )

        for struct_list in self._struct_lists.values():
            struct_list.setViewMode(QtWidgets.QListView.IconMode)

        main_structures = 'mainbuilds', 'background_decorations', 'dynamic_structures', 'spikes'
        for struct_type in main_structures:
            for path in glob.glob(f'resources/structures/{struct_type}/{biome}/*.st', recursive=True):
                res_name = path.replace('\\', '/').replace('resources/', '')
                self._add_structure(res_name, self._struct_lists[struct_type])

            for path in glob.glob(f'resources/structures/{struct_type}/{biome}/*.obj', recursive=True):
                res_name = path.replace('\\', '/').replace('resources/', '')
                self._add_structure(res_name, self._struct_lists[struct_type])

        others = 'foreground_decorations', 'decorations'
        for struct_type in others:

            for path in glob.glob(f'resources/{struct_type}/{biome}/*.obj'):
                res_name = path.replace('\\', '/').replace('resources/', '')
                self._add_structure(res_name, self._struct_lists[struct_type])

            for path in glob.glob(f'resources/{struct_type}/{biome}/*.st'):
                res_name = path.replace('\\', '/').replace('resources/', '')
                self._add_structure(res_name, self._struct_lists[struct_type])

        for path in glob.glob(f'resources/special_objects/*.obj'):
            res_name = path.replace('\\', '/').replace('resources/', '')
            self._add_structure(res_name, self._struct_lists['special_objects'])

    def _add_structure(self, res, struct_list, qimage=None):

        if qimage is None:
            qimage = self.window.load_image(res, self.palette)

        item_data = ItemData(res, qimage)

        item = QtWidgets.QListWidgetItem()
        icon = QtGui.QIcon()

        pixmap = QtGui.QPixmap(qimage)
        icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon)
        struct_list.addItem(item)

        self._item_to_data[id(item)] = item_data

    def add_structure_to_scene(self, item):
        data = self._item_to_data[id(item)]
        self.window.scene_handler.init_item(data.qimage, data.res)

    def new_structure(self):
        process = Popen("cmd.exe", shell=False, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        commands = '.\\commands\\activate.cmd\npython.exe structure_builder.py -e "" -g "" -w ""\n'
        out, err = process.communicate(commands)

        print(err, file=sys.stderr)

        parsed_data = self._parse_out_string(out)
        if parsed_data is not None:
            ground_string = parsed_data[0]
            walls_string = parsed_data[1]
            structure_text = parsed_data[2]

            name, ok = QtWidgets.QInputDialog.getText(self.window, 'Resource name',
                                                      'Enter the name of the resource:')
            if ok:
                if name:
                    if not name.endswith('.st'):
                        name += '.st'
                    name_template = self._tab_id_to_resource_name_template[
                        self.window.structures_tab.currentIndex()]
                    res_name = name_template.format(biome=self.biome, name=name)

                    with open(os.path.join('resources/', res_name), 'w') as file:
                        file.write(structure_text)

                    self._add_structure(res_name, self._struct_lists[
                        self._tab_id_to_structure_type[self.window.structures_tab.currentIndex()]])

                    self.window.file_handler.add_collision_data(res_name, ground_string, walls_string)

    @staticmethod
    def struct_list_items(struct_list):
        for i in range(struct_list.count()):
            yield struct_list.item(i)

    def remove_structure(self):
        struct_list = self._struct_lists[
                            self._tab_id_to_structure_type[self.window.structures_tab.currentIndex()]]
        item_to_remove = struct_list.currentItem()
        if item_to_remove is not None:
            removed_item_data = self._item_to_data.pop(id(item_to_remove))

            data_of_items = []
            for item in self.struct_list_items(struct_list):
                if item is not item_to_remove:
                    data_of_items.append(self._item_to_data.pop(id(item)))

            struct_list.clear()

            for item_data in data_of_items:
                self._add_structure(item_data.res, struct_list, item_data.qimage)

            os.rename(os.path.join('resources/', removed_item_data.res),
                      f'temp/trash/{int(time.time() * 100)}{os.path.basename(removed_item_data.res)}')

    @staticmethod
    def _parse_out_string(out):
        full_data = out.split('#####')
        if len(full_data) >= 3:
            data = full_data[1]
            structure_text = full_data[2]

            data = data.splitlines()
            ground_string = data[2]
            walls_string = data[3]

            while structure_text.startswith('\n'):
                structure_text = structure_text[1:]
            while structure_text.endswith('\n'):
                structure_text = structure_text[:-1]

            return ground_string, walls_string, structure_text
        return None

    def edit_current_structure(self):
        struct_list = self._struct_lists[
                            self._tab_id_to_structure_type[self.window.structures_tab.currentIndex()]]
        item_to_edit = struct_list.currentItem()
        if item_to_edit is not None:
            item_to_edit_data = self._item_to_data[id(item_to_edit)]

            process = Popen("cmd.exe", shell=False, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            commands = f'.\\commands\\activate.cmd\npython.exe structure_builder.py -e "{item_to_edit_data.res}"'

            raw_collision_data = self.window.file_handler.get_raw_collision_data(item_to_edit_data.res)

            if raw_collision_data == {}:
                raw_collision_data = {'ground': '', 'walls': ''}
            commands += f' -g "a{raw_collision_data["ground"]}"'
            commands += f' -w "a{raw_collision_data["walls"]}"'
            commands += '\n'

            out, err = process.communicate(commands)
            if err:
                print(err, file=sys.stderr)

            response = QtWidgets.QMessageBox.question(self.window, 'Edit structure',
                                                      "Do you want to save this version?",
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

            if response == QtWidgets.QMessageBox.Yes:
                parsed_data = self._parse_out_string(out)

                if parsed_data is not None:
                    ground_string = parsed_data[0]
                    walls_string = parsed_data[1]
                    structure_text = parsed_data[2]

                    res_name = item_to_edit_data.res

                    self.remove_structure()

                    with open(os.path.join('resources/', res_name), 'w') as file:
                        file.write(structure_text)

                    self._resource_loader.cache.pop(res_name)
                    self._add_structure(res_name, struct_list)

                    self.window.file_handler.add_collision_data(res_name, ground_string, walls_string)





