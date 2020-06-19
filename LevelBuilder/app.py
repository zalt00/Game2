# -*- coding:Utf-8 -*-

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from dataclasses import dataclass
from typing import Any
import sys
import json
import os
import importlib.util
from configparser import ConfigParser
from viewer.resources_loader import ResourcesLoader2
from pymunk.vec2d import Vec2d
from PIL import Image, ImageTk
import pygame
import yaml
pygame.init()


@dataclass()
class Structure:
    res_path: str
    img: Any
    pos: list
    state: str
    pilimage: Any
    name: str = ''
    scale: int = 1


class App(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        self.root = root
        super(App, self).__init__(root, *args, **kwargs)
        self.pack(fill='both', expand=True)

        self.rl = ResourcesLoader2('./../resources')
        self.palette = self.rl.load('forest/forest_structure_tilesets.stsp')

        self.canvas = tk.Canvas(self, width=1280, height=750, scrollregion=(0, 0, 5000, 2000), bg='#e4e4e4')
        self.canvas.grid(row=0, column=1, sticky='nesw')

        self.defilY = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.defilX = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.defilY.grid(row=0, column=0, sticky='ns')
        self.defilX.grid(row=1, column=1, sticky='ew')

        self.canvas['xscrollcommand'] = self.defilX.set
        self.canvas['yscrollcommand'] = self.defilY.set

        self.opt_frame = tk.Frame(self)
        self.opt_frame.grid(row=2, column=1, sticky='ew')

        self.set_bg_button = ttk.Button(self.opt_frame, text='Set BG', command=self.set_bg)
        self.set_bg_button.grid(row=0, column=0)

        self.add_structure_button = ttk.Button(self.opt_frame, text='Add Structure', command=self.add_structure)
        self.add_structure_button.grid(row=0, column=1)

        self.set_height_ref_button = ttk.Button(self.opt_frame, text='Set Height Ref', command=self.set_height_ref)
        self.set_height_ref_button.grid(row=0, column=2)

        self.save_as_button = ttk.Button(self.opt_frame, text='Save as', command=self.save_as)
        self.save_as_button.grid(row=0, column=3)

        self.import_button = ttk.Button(self.opt_frame, text='Import', command=self.import_structures)
        self.import_button.grid(row=0, column=4)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(2, weight=1)

        self.info_label_frame = tk.Frame(self)
        self.info_label_frame.columnconfigure(0, weight=1)
        self.info_label_frame.rowconfigure(3, weight=1)
        self.info_label_frame.grid(row=0, column=2, sticky='nsew')

        self.xylabel = tk.Label(self.info_label_frame, justify='left')
        self.xylabel.grid(row=0, column=0, sticky='nw')

        self.height_ref_label = tk.Label(self.info_label_frame, text='height ref: 0\n', justify='left')
        self.height_ref_label.grid(row=1, column=0, sticky='nw')

        self.focus_object_frame = tk.LabelFrame(self.info_label_frame, text='Focused Object')
        self.focus_object_frame.grid(row=2, column=0, sticky='nesw')

        self.preview_image = None
        self.preview_label = tk.Label(self.focus_object_frame)
        # self.preview_label.grid(row=0, column=0, sticky='nw')

        self.preview_canvas = tk.Canvas(self.focus_object_frame, width=0, height=0, scrollregion=(0, 0, 1200, 1200))
        self.preview_canvas.grid(row=0, column=0, sticky='nw')

        self.defilXpreview = tk.Scrollbar(
            self.focus_object_frame, orient='horizontal', command=self.preview_canvas.xview)

        self.defilYpreview = tk.Scrollbar(
            self.focus_object_frame, orient='vertical', command=self.preview_canvas.yview)

        self.preview_canvas['xscrollcommand'] = self.defilXpreview.set
        self.preview_canvas['yscrollcommand'] = self.defilYpreview.set

        self.struct_label = tk.Label(self.focus_object_frame, justify='left')
        self.struct_label.grid(row=2, column=0, sticky='nw')

        self.focus_object_frame.columnconfigure(0, weight=1)

        self.structure_list_var = tk.StringVar()
        self.listbox_elements = []
        self.structure_list = tk.Listbox(self.info_label_frame, selectmode='single',
                                         listvariable=self.structure_list_var)
        self.structure_list.grid(row=4, column=0, sticky='sew')

        self.txt_var = tk.StringVar()
        self.name_entry = tk.Entry(self.focus_object_frame, state='disabled', textvariable=self.txt_var)
        self.name_entry.grid(row=3, column=0, columnspan=2, sticky='ew')

        self.show_collision_var = tk.IntVar()
        self.show_collision_cbutton = ttk.Checkbutton(self.focus_object_frame,
                                                      text='Show default collision',
                                                      variable=self.show_collision_var,
                                                      command=self.show_collision_trigger)

        self.bind_all('<Motion>', self.mouse_motion)
        self.bind_all('<Button>', self.button_down)
        self.bind_all('<ButtonRelease>', self.button_up)
        self.bind_all('<KeyPress-Escape>', self.remove_focus)
        self.name_entry.bind('<KeyPress-Return>', self.change_name)
        self.bind_all('<KeyPress-Delete>', self.delete_structure)
        self.bind_all('<Control-c>', self.copy_struct)
        self.bind_all('<Control-v>', self.paste_struct)
        self.bind_all('<Control-s>', self.save)

        self.selection_rect_id = self.canvas.create_rectangle(0, 0, 0, 0, outline='red', width=2, tag='fg')

        self.state = 'idle'
        self.focus_on = None

        self.structures = dict()
        self.i = 0
        self.i2 = 0
        self.cache_structure = None

        self.cursor_pos = [0, 0]

        self.focus_dec = 0, 0

        self.bg = None
        self.bg_id = None
        self.ref_height = 0

        self.copied = None

        self.last_saved = None

        self.poly_visualisations = None
        self.ground_visualisations = None

    def button_up(self, evt):
        if self.state == 'moving structure':
            self.state = 'idle'

    def button_down(self, evt):
        if self.state == 'set height ref':
            self.ref_height = -self.canvas.canvasy(evt.y) + 720
            self.height_ref_label['text'] = 'height ref: {}\n'.format(self.ref_height)
            self.canvas['cursor'] = 'arrow'
            self.state = 'idle'

        elif self.state == 'placing structure':
            self.canvas['cursor'] = 'arrow'
            if self.cache_structure is not None:
                self.i += 1
                name = 'structure' + str(self.i)
                pos = list(self.cursor_pos)
                self.cache_structure.pos = pos
                id_ = self.canvas.create_image(pos[0], pos[1], image=self.cache_structure.img)
                self.structures[id_] = self.cache_structure
                self.cache_structure.name = name
                self.update_listvar()
            self.state = 'idle'
        elif evt.x_root <= 1280 and evt.y_root <= 750:
            s = self.canvas.find_overlapping(*self.cursor_pos, *self.cursor_pos)
            if len(s) > 0:
                s = set(s)
                if self.bg_id is not None:
                    for id_ in self.bg_id:
                        try:
                            s.remove(id_)
                        except KeyError:
                            pass
                try:
                    s.remove(self.selection_rect_id)
                except KeyError:
                    pass
                s = tuple(s)
                if len(s) == 0:
                    self.remove_focus(evt)
                else:
                    x, y = self.canvas.canvasx(evt.x), self.canvas.canvasy(evt.y)
                    struct_id = s[0]
                    x1, y1 = self.canvas.coords(struct_id)
                    self.focus_dec = x1 - x, y1 - y
                    struct = self.structures[struct_id]
                    self.select_structure(struct, struct_id)
                    self.state = 'moving structure'

        else:
            selection = self.structure_list.curselection()
            if len(selection) > 0:
                i = selection[0]
                struct_id = self.listbox_elements[i]
                struct = self.structures[struct_id]
                self.select_structure(struct, struct_id)

        self.mouse_motion(evt)

    def copy_struct(self, _):
        if self.focus_on is not None:
            self.copied = self.focus_on[0]

    def paste_struct(self, evt):
        if self.copied is not None:
            res_path = self.copied.res_path
            img = self.copied.img.copy()
            pilimage = self.copied.pilimage.copy()
            state = self.copied.state
            self.i += 1
            name = 'structure' + str(self.i)
            pos = list(self.copied.pos)
            struct = Structure(res_path, img, pos, state, pilimage, name)
            struct_id = self.canvas.create_image(*pos, image=img)
            self.structures[struct_id] = struct
            self.update_listvar()
            self.select_structure(struct, struct_id)
            self.mouse_motion(evt)

    def select_structure(self, struct, struct_id):
        self.focus_on = struct, struct_id
        preview_pilimage = struct.pilimage
        struct.scale = 1
        while preview_pilimage.width > 1000 or preview_pilimage.height > 1000:
            preview_pilimage = preview_pilimage.resize((preview_pilimage.width // 2, preview_pilimage.height // 2))
            struct.scale *= 2
        self.preview_image = ImageTk.PhotoImage(preview_pilimage)
        width, height = int(self.preview_image.width() + 10), int(self.preview_image.height() + 10)

        self.preview_canvas['width'] = width
        self.preview_canvas['height'] = height
        self.preview_canvas.create_image(width // 2, height // 2, image=self.preview_image)
        self.txt_var.set(struct.name)
        self.name_entry['state'] = 'normal'
        self.show_collision_cbutton.grid(row=4, column=0, sticky='ew')
        self.defilXpreview.grid(row=1, column=0, sticky='ew')
        self.defilYpreview.grid(row=0, column=1, sticky='ns')
        self.update_listbox_selection()

    def mouse_motion(self, evt):
        x, y = self.canvas.canvasx(evt.x), self.canvas.canvasy(evt.y)
        self.cursor_pos = x, y
        self.xylabel['text'] = 'x = {}, y = {}'.format(x, -self.ref_height + 720 - y)
        if self.state == 'moving structure':
            if evt.state & 0x0001:
                self.canvas.move(self.focus_on[1],
                                 self.cursor_pos[0] - self.focus_on[0].pos[0] + self.focus_dec[0], 0)
                self.focus_on[0].pos = self.cursor_pos[0] + self.focus_dec[0], self.focus_on[0].pos[1]

            elif evt.state & 0x0004:
                self.canvas.move(self.focus_on[1], 0,
                                 self.cursor_pos[1] - self.focus_on[0].pos[1] + self.focus_dec[1])
                self.focus_on[0].pos = self.focus_on[0].pos[0], self.cursor_pos[1] + self.focus_dec[1]

            else:
                self.canvas.move(self.focus_on[1],
                                 self.cursor_pos[0] - self.focus_on[0].pos[0] + self.focus_dec[0],
                                 self.cursor_pos[1] - self.focus_on[0].pos[1] + self.focus_dec[1])
                self.focus_on[0].pos = self.cursor_pos[0] + self.focus_dec[0], self.cursor_pos[1] + self.focus_dec[1]

        if self.focus_on is not None:
            x, y = self.focus_on[0].pos
            y = -self.ref_height + 720 - y

            x1, y1, x2, y2 = self.canvas.bbox(self.focus_on[1])
            y1 = -self.ref_height + 720 - y1
            y2 = -self.ref_height + 720 - y2
            self.struct_label['text'] = 'pos = ({}, {})\nres: {}\nstate: {}\nbbox: ({}, {}, {}, {})'.format(
                x, y, self.focus_on[0].res_path,
                self.focus_on[0].state, x1, y1, x2, y2)
            self.canvas.coords(self.selection_rect_id, *self.canvas.bbox(self.focus_on[1]))
        else:
            self.canvas.coords(self.selection_rect_id, 0, 0, 0, 0)
        self.canvas.tag_raise('fg')
        self.canvas.tag_lower('bg')
        self.preview_canvas.tag_raise('fg2')
        self.preview_canvas.tag_raise('fg1')

    def add_structure(self):
        filename = askopenfilename()
        if filename:
            res = self.rl.load_from_path(filename)
            res.build({'base': self.palette.build(res)})
            res_name = filename[filename.find('resources') + 10:]

            # awful, but no choice. Tkinter images are crap.
            pgimg = res.sheets['base']
            strimg = pygame.image.tostring(pgimg, 'RGBA')
            pilimage = Image.frombytes('RGBA', pgimg.get_size(), strimg)
            pilimage.save('temp.png')
            img = tk.PhotoImage(file='temp.png')

            pos = [0, 0]
            self.cache_structure = Structure(res_name, img, pos, 'base', pilimage)
            self.state = 'placing structure'
            self.canvas['cursor'] = 'crosshair'

    def set_height_ref(self):
        self.state = 'set height ref'
        self.canvas['cursor'] = 'crosshair'

    def set_bg(self):
        filename = askopenfilename()
        if filename:
            if self.bg_id is not None:
                for id_ in self.bg_id:
                    self.canvas.delete(id_)

            dir_name = os.path.dirname(filename)
            with open(filename) as file:
                data = json.load(file)

            self.bg = []
            self.bg_id = []
            for layer_data in data['background']:
                img = tk.PhotoImage(file=os.path.join(dir_name, layer_data['filename']))
                img = img.zoom(data['scale'])
                self.bg.append(img)
                self.bg_id.append(self.canvas.create_image(img.width() / 2, img.height() / 2, image=img, tag='bg'))
                layer_data['id'] = self.bg_id[-1]

            layers = sorted(data['background'], key=lambda d: d['layer'])
            for ld in layers:
                self.canvas.tag_raise(ld['id'])

    def remove_focus(self, evt):
        self.focus_on = None
        self.struct_label['text'] = '\n\n'
        self.preview_image = None
        for id_ in self.preview_canvas.find_all():
            self.preview_canvas.delete(id_)
        self.mouse_motion(evt)
        self.txt_var.set('')
        self.name_entry['state'] = 'disabled'
        self.show_collision_cbutton.grid_forget()
        self.preview_canvas['width'] = 1
        self.preview_canvas['height'] = 1
        self.defilXpreview.grid_forget()
        self.defilYpreview.grid_forget()
        self.show_collision_var.set(0)
        self.show_collision_trigger()
        self.structure_list.selection_clear(0, len(self.listbox_elements))

    def delete_structure(self, evt):
        if self.focus_on is not None:
            s_id = self.focus_on[1]
            self.canvas.delete(s_id)
            self.remove_focus(evt)
            self.structures.pop(s_id)
            self.update_listvar()

    def change_name(self, _):
        if self.focus_on is not None:
            self.focus_set()
            name = self.txt_var.get().replace(' ', '-')
            self.focus_on[0].name = name
            self.update_listvar()

    def update_listvar(self):
        self.structure_list_var.set(' '.join((v.name for v in self.structures.values())))
        self.listbox_elements[:] = list(self.structures.keys())

    def update_listbox_selection(self):
        if self.focus_on is not None:
            i = self.listbox_elements.index(self.focus_on[1])
            self.structure_list.selection_clear(0, len(self.listbox_elements))
            self.structure_list.selection_set(i)

    def save(self, *_, **__):
        if self.last_saved is not None:
            self._save(self.last_saved)
        else:
            self.save_as()

    def save_as(self, *_, **__):
        filename = asksaveasfilename(defaultextension='py')
        if filename:
            self._save(filename)
            self.last_saved = filename

    def _save(self, filename):
        txt = '# -*- coding:Utf-8 -*-\n\n'\
              'from utils.types import DataContainer\n'\
              'from pymunk.vec2d import Vec2d\n\n\n'\
              'class Objects(DataContainer):\n'
        structures = {self.transform_name(v.name): v for v in self.structures.values()}
        objects = repr(tuple(structures.keys()))
        txt += '    objects = ' + objects + '\n'
        for (name, struct), struct_id in zip(structures.items(), self.structures.keys()):
            x = int(struct.pos[0])
            y = int(-self.ref_height + 720 - self.canvas.bbox(struct_id)[3])

            poly, ground = self.get_collision_infos(struct)

            txt += """
    class {}:
        typ = 'structure'
        res = '{}'
        name = '{}'
        pos_x = {}
        pos_y = {}
        state = '{}'
        poly = {}
        ground = {}\n""".format(name, struct.res_path, struct.name, x, y, struct.state, poly, ground)

        with open(filename, 'w') as file:
            file.write(txt)

    def import_structures(self):
        filename = askopenfilename()
        if filename:
            self.i2 += 1
            spec = importlib.util.spec_from_file_location("structures{}".format(self.i2), filename)
            if spec is not None:
                structures_data = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(structures_data)
                data = structures_data.Objects
                for sn in data.objects:
                    struct_data = data.get(sn)
                    x = struct_data.pos_x
                    res_path = struct_data.res
                    state = struct_data.state
                    name = struct_data.name
                    while name in [v.name for v in self.structures.values()]:
                        name += '_'
                    cfg = ConfigParser()
                    cfg.read('config.ini', encoding="utf-8")
                    resources_base_dir = cfg['env']['resources_base_dir']
                    full_res_path = os.path.normpath(os.path.join(resources_base_dir, res_path))
                    img_path = os.path.normpath(os.path.join(full_res_path, state + '.png'))
                    img = tk.PhotoImage(file=img_path)
                    y = 720 - self.ref_height - struct_data.pos_y - img.height() // 2
                    struct = Structure(res_path, img, [x, y], state, name)
                    struct_id = self.canvas.create_image(x, y, image=img)
                    self.structures[struct_id] = struct
                    self.update_listvar()

    @staticmethod
    def get_collision_infos(struct):
        with open('default_collisions.yaml') as datafile:
            data = yaml.safe_load(datafile)
        struct_data = data.get(struct.res_path, None)
        if struct_data is not None:
            return struct_data['poly'], struct_data['ground']
        return

    def show_collision_trigger(self):
        if self.show_collision_var.get():
            if self.focus_on is not None:
                self.ground_visualisations = []
                self.poly_visualisations = []
                data = self.get_collision_infos(self.focus_on[0])
                if data is not None:
                    poly_ = data[0]
                    segments = data[1]
                    x = int(self.preview_canvas['width']) // 2
                    y = int(self.preview_canvas['height']) // 2 + self.preview_image.height() // 2
                    for points in poly_:
                        if len(points) > 0 and len(points[0]) > 0:
                            p = [
                                (int((dx / self.focus_on[0].scale) + x),
                                 int(y - (dy / self.focus_on[0].scale))) for dx, dy in points]

                            poly_visu_id = self.preview_canvas.create_polygon(*p, fill='',
                                                                              width=2, outline='#32b5fc', tag='fg2')
                            self.poly_visualisations.append(poly_visu_id)
                    for a, b in segments:
                        xa, ya = int(a[0] / self.focus_on[0].scale + x), int(y - a[1] / self.focus_on[0].scale)
                        xb, yb = int(b[0] / self.focus_on[0].scale + x), int(y - b[1] / self.focus_on[0].scale)
                        ground_visu_id = self.preview_canvas.create_line(xa, ya, xb, yb, fill='red', width=2, tag='fg1')
                        self.ground_visualisations.append(ground_visu_id)

        else:
            if self.poly_visualisations is not None:
                for pvisu in self.poly_visualisations:
                    self.preview_canvas.delete(pvisu)
                for gvisu in self.ground_visualisations:
                    self.preview_canvas.delete(gvisu)
                self.poly_visualisations = None
                self.ground_visualisations = None

    @staticmethod
    def transform_name(name):
        words = name.split('-')
        return ''.join(w.capitalize() for w in words)


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()

