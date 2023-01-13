###########################################
""" world manager """

# Imports
import glob

import map


# Parameters
_world = {'World': {}}  # initialization of master world dictionary
starting_position = (5, 10, 0)


def world_return():
    global _world
    return _world


def load_tiles(world_dict=None):
    """Parses a file that describes the world space into the _world object"""
    global _world
    _world['World'][(5, 10, 0)] = getattr(__import__('map'), 'Town')(5, 10, 0)
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
                _world['World'][(x, y, z)] = map.Wall(x, y, z) if tile_name == '' \
                    else getattr(__import__('map'), tile_name)(x, y, z)
                if world_dict is not None:
                    try:
                        _world['World'][(x, y, z)].visited = world_dict[(x, y, z)].visited
                    except KeyError:
                        pass


def tile_exists(x, y, z):
    global _world
    return _world['World'].get((x, y, z))


def save_world(world_dict):
    global _world
    _world = world_dict
