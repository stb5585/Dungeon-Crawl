###########################################
""" world manager """

# Imports
import os
import glob

# Parameters
_world = {'World': {}}
starting_position = (0, 0, 0)


def world_return():
    return _world


def load_tiles():
    """Parses a file that describes the world space into the _world object"""
    map_files = glob.glob('map_files/map_level_*')
    for map_file in map_files:
        z = map_file.split('_')[-1]
        z = int(z.split('.')[0])
        with open(map_file, 'r') as f:
            rows = f.readlines()
        x_max = len(rows[0].split('\t'))  # Assumes all rows contain the same number of tabs
        for y in range(len(rows)):
            cols = rows[y].split('\t')
            for x in range(x_max):
                tile_name = cols[x].replace('\n', '')  # Windows users may need to replace '\r\n'
                _world['World'][(x, y, z)] = None if tile_name == '' else getattr(__import__('map'), tile_name)(x, y, z)


def tile_exists(x, y, z):
    return _world['World'].get((x, y, z))
