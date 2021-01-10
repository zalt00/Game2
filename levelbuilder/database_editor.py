# -*- coding:Utf-8 -*-


import json
import tkinter as tk
from tkinter import ttk


def main():
    with open('collision_database.json') as datafile:
        data = json.load(datafile)

    root = tk.Tk()
    frames = []

    root.columnconfigure(0, weight=1)

    frame = tk.Frame(root)
    frame.columnconfigure(1, weight=1)

    label1 = tk.Label(frame, text='Resource names : ')
    label1.grid(row=0, column=0, sticky='ew')

    label2 = tk.Label(frame, text='Data :' + ' ' * 38)
    label2.grid(row=0, column=1, sticky='e')

    frame.grid(row=0, column=0, sticky='ew')

    update_frames(root, frames, data)

    save_button = ttk.Button(root, text='Save', command=lambda: save(data))
    save_button.grid(row=500, column=0, sticky='w')

    root.mainloop()


def save(data):
    with open('collision_database.json', 'w') as datafile:
        json.dump(data, datafile)


def get_button_command(root, res_name, data, frames):
    def callback():
        data.pop(res_name)
        update_frames(root, frames, data)
    return callback


def update_frames(root, frames, data):
    for frame in frames:
        frame.grid_remove()

    frames.clear()

    for i, res_name in enumerate(sorted(data)):
        frame = tk.Frame(root)
        frame.columnconfigure(1, weight=1)
        label = tk.Label(frame, text=res_name)
        label.grid(row=0, column=0, sticky='ew')

        text = ''
        if 'walls' in data[res_name]:
            text += 'walls'
            if 'ground' in data[res_name]:
                text += ', ground'
        elif 'ground' in data[res_name]:
            text += 'ground'
        else:
            text += 'empty'
        label2 = tk.Label(frame, text=text)
        label2.grid(row=0, column=1, sticky='e')

        button = ttk.Button(frame, text='Delete', command=get_button_command(root, res_name, data, frames))
        button.grid(row=0, column=2, sticky='e')

        frame.grid(row=i + 1, column=0, sticky='ew')

        frames.append(frame)



if __name__ == '__main__':
    main()
