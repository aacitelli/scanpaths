from common.defs import vertex, segment, bbox
from random import shuffle 
from math import ceil, fmod
import copy

# Intended Use Case:
# One Island() object is declared for the whole part.
# The 
class Island():

    # Constructed with anything that doesn't change layer-by-layer 
    def __init__(self, island_size=10, island_offset=1, island_overlap=.25):
        self.island_size = island_size
        self.island_offset = island_offset
        self.island_overlap = island_overlap

    # Splits the provided list of vertices along overall lines
    # segment_list: List of segments signifying our vectors 
    # layer_num: Exactly what you think it is
    # hatch_angle: Exactly what you think it is. 
    #   Specifically, slice_layer will be called twice by the caller, with hatch_angle=0 the first time and hatch_angle=90 the second time.
    # bbox: object with tl, tr, bl, br, width, height fields
    def slice_layer(self, segment_list, layer_num, hatch_angle, bbox):

        # Output variable 
        sliced_segment_list = []

        # Things that change layer-by-layer 
        self.layer_num = layer_num 
        self.hatch_angle = hatch_angle
        self.bbox = bbox 
        self.apply_offset(self.bbox, self.island_size, self.island_offset * layer_num) 
        self.grid_width = ceil(self.bbox.width / self.island_size)
        self.grid_height = ceil(self.bbox.width / self.island_size)

        # Generate island order for this layer, then iterate through it
        # Note that the C++ implementation filters from in here, whereas the Python version filters during the generation of the island order
        island_order = self.gen_island_order()
        for island_coords in island_order:
            island_bbox = self.fill_island_coords(island_coords, self.island_overlap) # Get absolute coords for the given island; also pads based on overlap

            # Iterate through all segments and add the subsegment that intersects to end array 
            for segment in segment_list:
                intersecting_segment = self.get_intersecting_segment(segment, island_bbox)
                if intersecting_segment != None:
                    sliced_segment_list.append(intersecting_segment)

        return sliced_segment_list

    # Given a set of coords, returns absolute coordinates with those and applies overlap 
    def fill_island_coords(self, coords, overlap):
        output_bbox = bbox()
        output_bbox.bl.x = self.bbox.bl.x + coords.x * self.island_size - overlap/2
        output_bbox.bl.y = self.bbox.bl.y + coords.y * self.island_size - overlap/2 
        output_bbox.tr.x = output_bbox.bl.x + self.island_size + overlap
        output_bbox.tr.y = output_bbox.bl.y + self.island_size + overlap 
        output_bbox.tl.x = output_bbox.bl.x 
        output_bbox.tl.y = output_bbox.tr.y 
        output_bbox.br.x = output_bbox.tr.x 
        output_bbox.br.y = output_bbox.bl.y 
        return output_bbox 

    def get_intersecting_segment(self, segment, island_bbox):
        return segment # Placeholder 

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

    # Generates random grid order to iterate through this layer 
    def gen_island_order(self):

        # We append to this throughout the method then return it 
        arr = []

        # Depending on our layer/hatch angle, we only keep certain islands 
        # Even Layer, Horizontal or Odd Layer, Vertical = Evens on Even Rows, Odds on Odd Rows
        # Even Layer, Vertical or Odd Layer, Horizontal = Odds on Even Rows, Evens on Odd Rows 
        if self.layer_num % 2 == 0 and self.hatch_angle == 0 or self.layer_num % 2 == 1 and self.hatch_angle == 90:
            even_start, odd_start = 0, 1
        else:
            even_start, odd_start = 1, 0

        # Actually generate the list of possible coordinates 
        for y in range(0, self.grid_height, 2): # Even Rows
            for x in range(even_start, self.grid_width, 2): 
                arr.append(vertex(x, y))
        for y in range(1, self.grid_height, 2): # Odd Rows
            for x in range(odd_start, self.grid_width, 2): 
                arr.append(vertex(x, y))

        # Shuffle and return 
        shuffle(arr)
        return arr 