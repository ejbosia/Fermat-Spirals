'''

'''

import src.utilities.shapely_utilities as SU

def test_distance_transform():
    pass

'''
Distance transform without changing holes
'''
def test_distance_transform_diff():
    pass

# not testing plotting functions


'''
Cut a linestring at a specified distance. This always returns at least one linestring and a None, or two linestrings
'''
def test_cut():
   pass


'''
Reformat the linestring so position 0 is the start point. This may involve inserting a new point into the contour.
'''
def test_cycle():
    pass


'''
Find any self intersections in the input linestring
'''
def test_self_intersections():
    pass


'''
Find any self intersections in the input linestring using binary search like recursion
'''
def test_self_intersections_binary(ls):
    pass


'''
Reverse a input linestring ~ this is helpful for projection when the distance is ambiguous (intersections)
'''
def test_reverse(ls):
    pass


'''
Merge two linestrings
'''
def test_merge(ls1, ls2):
    pass


'''
Evenly sample the linestring ~ this returns a list of points
'''
def test_sample(ls, distance):
    pass


'''
Create a virtual boundary around a polygon ~ returns the exterior and a list of interiors
'''
def test_virtual_boundary(polygon, distance):
    pass