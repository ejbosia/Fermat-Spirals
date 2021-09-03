'''

'''

import src.utilities.shapely_utilities as SU

from shapely.geometry import LineString, Point

'''
Create a list of linestrings for testing
'''
def generate_linestrings():
    pass



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

    # create a linestring
    ls = LineString([(0,0),(10,0),(10,10),(20,10)])

    # test a normal cut
    start, end = SU.cut(ls, 15)

    assert start.length == 15
    assert end.length == ls.length - 15
    assert start.coords[-1] == end.coords[0]

    # test cutting on the start
    start, end = SU.cut(ls, 0)
    assert start is None
    assert end == ls

    # test cutting on the end
    start, end = SU.cut(ls, ls.length)
    assert start == ls
    assert end is None

    # test cutting a negative distance
    start, end = SU.cut(ls,-1)
    assert start is None
    assert end == ls

    # test cutting farther than the length
    start, end = SU.cut(ls, ls.length+1)
    assert start == ls
    assert end is None



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