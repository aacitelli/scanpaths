from common.defs import vertex, segment, bbox
from random import shuffle 
from math import ceil 
import copy

class Island():

    def __init__(self, layer_num, hatch_angle, bbox, island_size=10, island_offset=1, island_overlap=.25):
        self.layer_num = layer_num 
        self.bbox = bbox 
        self.apply_offset(self.bbox, island_size, island_offset) 
        self.island_size = island_size 
        self.island_offset = island_offset 
        self.island_overlap = island_overlap 
        self.grid_width = ceil(self.bbox.width / self.island_size)
        self.grid_height = ceil(self.bbox.width / self.island_size)

    # Splits the provided list of vertices along overall lines
    # segment_list: List of segments signifying our vectors 
    # bbox: object with tl, tr, bl, br, width, height fields 
    def exec(self, segment_list):

        # Generate island order for this layer, then iterate through it 
        island_order = self.gen_island_order(self.grid_width, self.grid_height, self.layer_num)
        for island_coords in island_order:
            pass 

    # Given island size and an amount to offset by, performs the offset 
    # Offset up-right, then iterate down-left until we get to something >= size of original bbox 
    # TODO: There's a constant-time way to do this that isn't even much math, implement it 
    def apply_offset(self, bbox, island_size, island_offset):
        backup = copy.deepcopy(bbox)
        bbox.bl.x += island_offset 
        bbox.bl.y += island_offset 
        while bbox.bl.x > backup.bl.x:
            bbox.bl.x -= island_size 
            bbox.bl.y -= island_size 
        bbox.br.y = bbox.bl.y 
        bbox.tl.x = bbox.bl.x

    # Generates random grid order to iterate through 
    def gen_island_order(self, width, height, hatchAngle):
        arr = []
        for x in range(width):
            for y in range(height):
                arr.append(vertex(x, y))
        shuffle(arr)
        return arr 