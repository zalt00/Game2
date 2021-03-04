# -- codingUtf-8 --

from structurebuilder.app import App
import argparse
import sys

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--edit', type=str)
    parser.add_argument('-g', '--groundcollision', type=str)
    parser.add_argument('-w', '--wallscollision', type=str)
    args = parser.parse_args()

    a = App(1200, 800, 'resources', structure_to_edit=args.edit, ground_collision=args.groundcollision[1:],
            walls_collision=args.wallscollision[1:])
    a.run()
