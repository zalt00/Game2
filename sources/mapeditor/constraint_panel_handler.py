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

        self.window.constraints_scroll_area_content.layout().addWidget(widget)
        self.constraints.append(widget)
        widget.update_widget()

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






