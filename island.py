from common.defs import Vertex, Segment, BoundingBox
from common.lines import line_intersects_line
from random import shuffle 
from math import ceil, fmod
from copy import deepcopy 
import numpy
import sys 

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
    # segment_list: numpy array of segments signifying our vectors 
    # layer_num: Exactly what you think it is
    # hatch_angle: Exactly what you think it is. 
    #   Specifically, slice_layer will be called twice by the caller, with hatch_angle=0 the first time and hatch_angle=90 the second time.
    # bbox: object with tl, tr, bl, br, width, height fields
    def slice_layer(self, segment_list, layer_num: int, hatch_angle: float, bbox: BoundingBox):

        # Output variable 
        sliced_segment_list = []

        # Things that change layer-by-layer 
        self.layer_num = layer_num 
        self.hatch_angle = hatch_angle
        self.bbox = bbox 
        self.apply_offset(self.bbox, self.island_size, self.island_offset * layer_num) 
        self.grid_width = ceil(self.bbox.width / self.island_size)
        self.grid_height = ceil(self.bbox.height / self.island_size)

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
    def fill_island_coords(self, coords: Vertex, overlap: float):
        output_bbox = BoundingBox()
        output_bbox.bl.x = self.bbox.bl.x + coords.x * self.island_size - overlap/2
        output_bbox.bl.y = self.bbox.bl.y + coords.y * self.island_size - overlap/2 
        output_bbox.tr.x = output_bbox.bl.x + self.island_size + overlap
        output_bbox.tr.y = output_bbox.bl.y + self.island_size + overlap 
        output_bbox.tl.x = output_bbox.bl.x 
        output_bbox.tl.y = output_bbox.tr.y 
        output_bbox.br.x = output_bbox.tr.x 
        output_bbox.br.y = output_bbox.bl.y 
        return output_bbox 

    # Returns the overlapping segment if overlap exists, None otherwise 
    def get_intersecting_segment(self, segment: Segment, bbox: BoundingBox):

        # Get segments representing the sides 
        top = Segment(bbox.tl, bbox.tr)
        bottom = Segment(bbox.bl, bbox.br)
        left = Segment(bbox.tl, bbox.bl)
        right = Segment(bbox.tr, bbox.br)

        # Colinearity with bottom special case
        if segment.v1.y == segment.v2.y and segment.v1.y == bbox.bl.y:
            
            # No Overlap
            if segment.v1.x <= bbox.tl.x and segment.v2.x <= bbox.tl.x or \
                segment.v1.x >= bbox.tl.x and segment.v2.x >= bbox.tl.x:
                return False 
            
            # Determine endpoints
            left_point = segment.v1 if segment.v1.x <= segment.v2.x else segment.v2
            right_point = segment.v2 if segment.v1.x <= segment.v2.x else segment.v1 
            left = max(left_point.x, bbox.tl.x)
            right = min(right_point.x, bbox.tr.x)     
            return Segment(left, right)   
                
        # Exclude colinearity with top special case 
        if segment.v1.y == segment.v2.y and segment.v1.y == bbox.tl.y:
            return False 

        # Colinearity with left special case
        if segment.v1.x == segment.v2.x and segment.v1.x == bbox.bl.x:
            
            # No Overlap
            if segment.v1.y <= bbox.tl.y and segment.v2.y <= bbox.tl.y or \
                segment.v1.y >= bbox.tl.y and segment.v2.y >= bbox.tl.y:
                return False 
            
            # Determine endpoints
            bottom_point = segment.v1 if segment.v1.y <= segment.v2.y else segment.v2
            top_point = segment.v2 if segment.v1.y <= segment.v2.y else segment.v1 
            bottom = max(bottom_point.y, bbox.bl.y)
            top = min(top_point.x, bbox.tl.y)     
            return Segment(bottom, top)   
                
        # Exclude colinearity with right special case 
        if segment.v1.x == segment.v2.x and segment.v1.x == bbox.tr.x:
            return False

        # Calc intersection points
        top_intersection = line_intersects_line(top, segment)
        bottom_intersection = line_intersects_line(bottom, segment)
        left_intersection = line_intersects_line(left, segment)
        right_intersection = line_intersects_line(right, segment)

        # As line_intersects_line just checks if the infinite extension of the lines intersects,
        # we check if the intersection bounds are actually on our segments
        intersects_top = top_intersection != None and \
            (top_intersection.x >= bbox.tl.x and top_intersection.x <= bbox.tr.x) and \
            ((segment.v1.y <= bbox.tl.y and segment.v2.y >= bbox.tl.y) or \
            (segment.v1.y >= bbox.tl.y and segment.v2.y <= bbox.tl.y))
        intersects_bottom = bottom_intersection != None and \
            (bottom_intersection.x >= bbox.tl.x and bottom_intersection.x <= bbox.tr.x) and \
            ((segment.v1.y <= bbox.bl.y and segment.v2.y >= bbox.bl.y) or \
            (segment.v1.y >= bbox.bl.y and segment.v2.y <= bbox.bl.y))
        intersects_right = right_intersection != None and \
            (right_intersection.y >= bbox.bl.y and right_intersection.y <= bbox.tl.y) and \
            ((segment.v1.x <= bbox.tr.x and segment.v2.x >= bbox.tr.x) or \
            (segment.v1.x >= bbox.tr.x and segment.v2.x <= bbox.tr.x))
        intersects_left = left_intersection != None and \
            (left_intersection.y >= bbox.bl.y and left_intersection.y <= bbox.tl.y) and \
            ((segment.v1.x <= bbox.tl.x and segment.v2.x >= bbox.tl.x) or \
            (segment.v1.x >= bbox.tl.x and segment.v2.x <= bbox.tl.x))
        num_intersections = intersects_top + intersects_bottom + intersects_right + intersects_left 

        # Zero-Intersections case either means both points are inside or no points are inside 
        if num_intersections == 0:
            if segment.v1.x < bbox.tl.x or segment.v1.x > bbox.tr.x or \
                segment.v1.y < bbox.bl.y or segment.v1.y > bbox.tl.y:
                return False 
            return Segment(segment.v1, segment.v2)

        # One-Intersection case means our subsegment is the point inside the rectangle to the point intersecting the rectangle 
        elif num_intersections == 1:
            output = Segment()
            
            # Figure out which point is inside the bbox
            if segment.v1.x >= bbox.tl.x and segment.v1.x <= bbox.tr.x and \
                segment.v1.y >= bbox.bl.y and segment.v1.y <= bbox.tl.y:
                output.v1 = deepcopy(segment.v1)
            else:
                output.v1 = deepcopy(segment.v2)

            # Get other point as the intersection 
            if intersects_top:
                output.v2 = deepcopy(top_intersection):
            elif intersects_right: 
                output.v2 = deepcopy(right_intersection)
            elif intersects_bottom:
                output.v2 = deepcopy(bottom_intersection)
            else:
                output.v2 = deepcopy(left_intersection)

        # Ensure we aren't exactly on a corner, with the other one outside the bbox 
        if num_intersections == 2:

            # Check Top-Right 
            if intersects_top and intersects_right and \
                self.vertices_equal(segment.v1, bbox.tr) and not self.point_in_bbox(segment.v2, bbox) or \
                self.vertices_equal(segment.v2, bbox.tr) and not self.point_in_bbox(segment.v1, bbox):
                return False 

            # Check Top-Left
            if intersects_top and intersects_left and \
                self.vertices_equal(segment.v1, bbox.tl) and not self.point_in_bbox(segment.v2, bbox) or \
                self.vertices_equal(segment.v2, bbox.tl) and not self.point_in_bbox(segment.v1, bbox):
                return False 

            # Check Bottom-Right 
            if intersects_bottom and intersects_right and \
                self.vertices_equal(segment.v1, bbox.br) and not self.point_in_bbox(segment.v2, bbox) or \
                self.vertices_equal(segment.v2, bbox.br) and not self.point_in_bbox(segment.v1, bbox):
                return False 

            # Check Bottom-Left 
            if intersects_bottom and intersects_left and
                self.vertices_equal(segment.v1, bbox.bl) and not self.point_in_bbox(segment.v2, bbox) or \
                self.vertices_equal(segment.v2, bbox.bl) and not self.point_in_bbox(segment.v1, bbox):
                return False 

        # Two-Intersection Case (Including Duplicates)
        elif num_intersections >= 2 and num_intersections <= 4:
            first_filled, second_filled = False, False 
            output = Segment()

            # Top Intersection 
            if intersects_top: 
                output.v1 = deepcopy(top_intersection)
                first_filled = True

            # Bottom Intersection
            if intersects_bottom:
                if first_filled and not self.vertices_equal(output.v1, bottom_intersection):
                    output.v2 = deepcopy(bottom_intersection)
                    secondFilled = True
                elif not first_filled:
                    output.v1 = deepcopy(bottom_intersection)
                    firstFilled = True 

            # Right Intersection 
            if not second_filled and intersects_right:
                if first_filled and not self.vertices_equal(output.v1, right_intersection)
                    output.v2 = deepcopy(right_intersection)
                    second_filled = True
                elif not first_filled:
                    output.v1 = deepcopy(right_intersection)
                    first_filled = True 

            # Left Intersection 
            if not second_filled and intersects_left:
                if first_filled and not self.vertices_equal(output.v1, left_intersection)
                    output.v2 = deepcopy(left_intersection)
                    second_filled = True
                elif not first_filled:
                    output.v1 = deepcopy(left_intersection)
                    first_filled = True 

            # Error case that provides more debug information 
            if not second_filled:
                print("ERR (get_intersecting_segment): Got through 2/3/4 intersection code without two intersections!", file=sys.stderr)
                return False 

        else:
            print("ERR (get_intersecting_segment): Unrecognized number of intersections!", file=sys.stderr)
            return False 

        # Assume we found output; we would have errored out if we ran into issues otherwise 
        return True 
    
    def point_in_bbox(v: Vertex, bbox: BoundingBox) -> bool:
        return v.x >= bbox.tl.x and v.x <= bbox.tr.x and v.y >= bbox.bl.y and v.y <= bbox.tl.y

    def vertices_equal(v1: Vertex, v2: Vertex) -> Vertex:
        return v1.x = v2.x and v1.y = v2.y

    # Given island size and an amount to offset by, performs the offset 
    # Offset up-right, then iterate down-left until we get to something >= size of original bbox 
    # TODO: There's a constant-time way to do this that isn't even much math, implement it 
    def apply_offset(self, bbox: BoundingBox, island_size: float, island_offset: float) -> None:
        backup = deepcopy(bbox)
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
        arr = numpy.array([])

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
                numpy.append(arr, Vertex(x, y))
        for y in range(1, self.grid_height, 2): # Odd Rows
            for x in range(odd_start, self.grid_width, 2): 
                numpy.append(arr, Vertex(x, y))

        # Shuffle and return 
        shuffle(arr)
        return arr 