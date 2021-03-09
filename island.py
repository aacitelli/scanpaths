from common.defs import vertex, segment, bbox
from random import shuffle 
from math import ceil 
import copy

# Splits the provided list of vertices along overall lines
# segment_list: List of segments signifying our vectors 
# bbox: object with tl, tr, bl, br, width, height fields 
def island(segment_list, bbox, island_size, island_offset, island_overlap):

    # Generate order to iterate through islands 
    grid_width = ceil(bbox.width / island_size)
    grid_height = ceil(bbox.width / island_size)
    island_order = gen_island_order(grid_width, grid_height)

    # Do offset (pass by value)
    apply_offset(bbox, island_size, island_offset)

# Given island size and an amount to offset by, performs the offset 
# Offset up-right, then iterate down-left until we get to something >= size of original bbox 
def apply_offset(bbox, island_size, island_offset):
    backup = copy.deepcopy(bbox)
    bbox.bl.x += island_offset 
    bbox.bl.y += island_offset 
    while bbox.bl.x > backup.bl.x:
        bbox.bl.x -= island_size 
        bbox.bl.y -= island_size 
    bbox.br.y = bbox.bl.y 
    bbox.tl.x = bbox.bl.x

# Generates random grid order to iterate through 
def gen_island_order(width, height):
    arr = []
    for x in range(width):
        for y in range(height):
            arr.append(vertex(x, y))
    shuffle(arr)
    return arr 

vertex_list = []
bbox = bbox(vertex(), vertex(), vertex(), vertex())
island_size = 4
island_offset = 1.25
island_overlap = 0
island(vertex_list, bbox, island_size, island_offset, island_overlap)