# -*- coding:Utf-8 -*-


from PyQt5 import QtWidgets
from .constraint_panel_widgets import ConstraintFrame


class ConstraintPanelHandler:
    def __init__(self, window):
        self.window = window

        self.constraints = []

    def add_constraint(self, name='', anchor_a=(0, 0), anchor_b=(0, 0), object_a='', object_b=''):
        if name == '':
            identifier = self.window.generate_identifier()
            name = f'constraint{identifier}'
        widget = ConstraintFrame(self.window.scene_handler.graphics_view_items,
                                 name=name,
                                 anchor_a=anchor_a,
                                 anchor_b=anchor_b,
                                 object_a=object_a,
                                 object_b=object_b)
        widget.remove_callback = self.get_remove_callback(widget)
        widget.display_callback = self.display_constraint

        self.window.constraints_scroll_area_content.layout().addWidget(widget)
        self.constraints.append(widget)
        widget.update_widget()

    def display_constraint(self, value, widget):
        if value:
            item1 = self.window.scene_handler.graphics_view_items[widget.name_to_id[widget.object_a]][0]
            item2 = self.window.scene_handler.graphics_view_items[widget.name_to_id[widget.object_b]][0]

            rect1 = item1.boundingRect()
            x1 = self.window.canvasx2datax(item1.x(), rect1)
            y1 = self.window.canvasy2datay(item1.y(), rect1)

            rect2 = item2.boundingRect()
            x2 = self.window.canvasx2datax(item2.x(), rect2)
            y2 = self.window.canvasy2datay(item2.y(), rect2)

            anchor_a = widget.anchor_a
            anchor_b = widget.anchor_b

            x1 += anchor_a[0]
            x2 += anchor_b[0]
            y1 += anchor_a[1]
            y2 += anchor_b[1]

            # cx1 = self.window.datax2canvasx(x1, rect1)
            # cy1 = self.window.datay2canvasy(y1, rect1)
            # cx2 = self.window.datax2canvasx(x2, rect2)
            # cy2 = self.window.datay2canvasy(y2, rect2)

            line = self.window.scene_handler.display_constraint_line((x1, -y1), (x2, -y2))
            widget.scene_line = line

        else:
            if widget.scene_line is not None:
                self.window.scene_handler.remove_constraint_line(widget.scene_line)
                widget.scene_line = None

    def get_remove_callback(self, widget):
        def remove():
            self.window.constraints_scroll_area_content.layout().removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
            self.constraints.remove(widget)
        return remove

    def update_constraints(self):
        for widget in self.constraints:
            widget.reinit_all_comboboxes()

    def apply_changes(self):
        for widget in self.constraints:
            widget.update_data()

    def add_constraint_slot(self):
        self.add_constraint()

    def get_data(self, objects_data):
        data = dict()
        for widget in self.constraints:
            widget.update_data()

            key = widget.name + '_constraint'
            while key in data:
                widget.name += '_'
                key = widget.name + '_constraint'

            obj_a_key = f'{widget.object_a}_structure'
            obj_b_key = f'{widget.object_b}_structure'
            if obj_a_key in objects_data and obj_b_key in objects_data:
                if 'walls' in objects_data[obj_a_key] and 'walls' in objects_data[obj_b_key]:

                    constraint_data = dict()
                    data[key] = constraint_data

                    constraint_data['name'] = widget.name
                    constraint_data['object_a'] = widget.object_a
                    constraint_data['object_b'] = widget.object_b

                    constraint_data['res'] = widget.resource
                    constraint_data['type'] = 'constraint'

                    constraint_data['anchor_a'] = list(widget.anchor_a)
                    constraint_data['anchor_b'] = list(widget.anchor_b)

                else:
                    print(f'error - can not add the constraint {key} to an object without collision data')
            else:
                print(f'error - objects of constraint {key} not in objects_data')

        return data






